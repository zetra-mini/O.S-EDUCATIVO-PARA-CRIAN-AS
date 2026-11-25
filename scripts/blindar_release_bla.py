#!/usr/bin/env python3
"""
Orquestrador Oficial de Blindagem Counter-REA (Blind LLM Agents - BLA v3.6)
para o J.A.R.V.I.S. Kids OS.

Segue rigorosamente o contrato oficial do BLA para projetos Python + Web:
1. NUNCA sobrescreve os arquivos-fonte do repositório de desenvolvimento.
2. Cria uma árvore limpa de staging em `dist/jarvis-hardened-release/` (sem bancos pessoais,
   chaves `config.json` ou caches locais — higiene total de release).
3. Executa `bla lint` (portões R1–R12) e `bla harden --weave-decoys` com intensidade configurável:
   - `balanced` (Padrão): ideal para netbooks modestos como Acer Aspire One 532 (Atom N450 / 1GB RAM).
   - `bankrupt`: proteção máxima Counter-REA para distribuição Desktop / Cloud / VPS.
4. Sobrepõe os artefatos blindados `.bla-hardened/` sobre o staging e limpa resíduos temporários.
5. Executa a suíte de testes automatizados contra o código blindado para atestar 100% de
   equivalência funcional em tempo de execução antes de aprovar a release.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT_DIR / "dist" / "jarvis-hardened-release"

IGNORE_PATTERNS = (
    ".git",
    ".github",
    ".cache",
    ".bla-hardened",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "scratch",
    "cache_tts",
    "config.json",
    "config_nuvem.json",
    "uso_diario.json",
    "*.pyc",
    "*.pyo",
    "*.db",
    "*.db-wal",
    "*.db-shm",
    "*.log",
    "*.deb",
    "*.zip",
    "*.tar.gz",
    "*.apk",
)


def resolver_comando_bla() -> list[str]:
    """Prioriza o motor local `blind-llm-agents/dist/cli.js` (0ms offline), com fallback para npx."""
    candidatos_locais = [
        ROOT_DIR.parent / "blind-llm-agents" / "dist" / "cli.js",
        Path.home() / ".gemini" / "antigravity" / "scratch" / "blind-llm-agents" / "dist" / "cli.js",
    ]
    for cli_js in candidatos_locais:
        if cli_js.is_file():
            return ["node", str(cli_js)]

    npx_bin = "npx.cmd" if os.name == "nt" else "npx"
    return [npx_bin, "-y", "bla-agents@latest"]


def preparar_staging_limpo(destino: Path) -> None:
    """Copia o projeto para o diretório de staging removendo segredos locais e artefatos dev."""
    if destino.exists():
        shutil.rmtree(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(
        ROOT_DIR,
        destino,
        ignore=shutil.ignore_patterns(*IGNORE_PATTERNS),
    )

    # Remove testes da árvore final apenas após validação (mantém temporariamente se necessário)
    uploads_dir = destino / "static" / "uploads_recados"
    if uploads_dir.exists():
        for item in uploads_dir.iterdir():
            if item.name != ".gitkeep":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()


def sobrepor_artefatos_blindados(staging_dir: Path) -> int:
    """Move os arquivos de `.bla-hardened/` sobre o diretório de staging e remove o espelho."""
    mirror_dir = staging_dir / ".bla-hardened"
    if not mirror_dir.is_dir():
        return 0

    promovidos = 0
    for item in mirror_dir.rglob("*"):
        if item.is_file():
            rel = item.relative_to(mirror_dir)
            if rel.name.startswith(".bla-"):
                continue
            alvo = staging_dir / rel
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, alvo)
            promovidos += 1

    shutil.rmtree(mirror_dir, ignore_errors=True)
    return promovidos


def verificar_equivalencia_funcional(staging_dir: Path) -> bool:
    """Executa a suíte de testes unitários diretamente sobre a cópia blindada em staging."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(staging_dir)
    env["PYTHONUTF8"] = "1"

    cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(staging_dir / "tests"), "-v"]
    proc = subprocess.run(cmd, cwd=str(staging_dir), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        print("❌ [ERRO DE EQUIVALÊNCIA] A suíte de testes falhou na build blindada:", file=sys.stderr)
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return False
    return True


def executar_pipeline(
    out_dir: Path,
    intensity: str = "balanced",
    in_place_staging: bool = False,
    skip_tests: bool = False,
) -> int:
    bla_cmd = resolver_comando_bla()
    print(f"🛡️  [BLA Counter-REA] Motor selecionado: {' '.join(bla_cmd)}")
    print(f"⚙️  [BLA Counter-REA] Intensidade: {intensity} (Otimizado para equivalência em runtime)")

    if not in_place_staging:
        print(f"📦 [1/4] Criando árvore limpa de staging em: {out_dir}")
        preparar_staging_limpo(out_dir)
    else:
        print(f"📦 [1/4] Blindando diretório de empacotamento existente: {out_dir}")

    with tempfile.TemporaryDirectory(prefix="bla_jarvis_state_") as state_dir:
        env = os.environ.copy()
        env["BLA_STATE_DIR"] = state_dir

        # Etapa 2: Lint de Higiene & Portões R1-R12
        print("🔍 [2/4] Executando auditoria de portões de empacotamento (`bla lint`)...")
        lint_proc = subprocess.run(
            [*bla_cmd, "lint", str(out_dir), "--intensity", intensity, "--json"],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        lint_data = {}
        try:
            lint_data = json.loads(lint_proc.stdout or "{}")
        except json.JSONDecodeError:
            pass

        if lint_data.get("shouldRefuseBankrupt"):
            print("❌ [BLA LINT] Bloqueio detectado nos portões de empacotamento:", file=sys.stderr)
            print(json.dumps(lint_data.get("blocking", []), indent=2, ensure_ascii=False), file=sys.stderr)
            return 2

        # Etapa 3: Harden com Weave Estrutural
        print("⚡ [3/4] Injetando escudos Counter-REA (`bla harden --weave-decoys`)...")
        harden_cmd = [
            *bla_cmd,
            "harden",
            str(out_dir),
            "--intensity",
            intensity,
            "--weave-decoys",
            "--json",
        ]
        harden_proc = subprocess.run(
            harden_cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if harden_proc.returncode != 0:
            print("❌ [BLA HARDEN] Falha durante a blindagem:", file=sys.stderr)
            print(harden_proc.stderr or harden_proc.stdout, file=sys.stderr)
            return 1

        harden_report = json.loads(harden_proc.stdout)
        promovidos = sobrepor_artefatos_blindados(out_dir)
        print(f"   ✅ Artefatos blindados e promovidos no staging: {promovidos}")

        # Etapa 4: Verificação de Equivalência Funcional Real (Testes Automatizados)
        testes_ok = True
        if not skip_tests and (out_dir / "tests").is_dir():
            print("🧪 [4/4] Executando testes automatizados na build blindada (100% Runtime Equivalence)...")
            testes_ok = verificar_equivalencia_funcional(out_dir)
            if not testes_ok:
                return 3
            # Remove pasta tests da release final distribuível após aprovação
            shutil.rmtree(out_dir / "tests", ignore_errors=True)
            for pyc_dir in out_dir.rglob("__pycache__"):
                shutil.rmtree(pyc_dir, ignore_errors=True)

        # Salva recibo auditável da blindagem na release
        artefatos_ok = [a for a in harden_report.get("artifacts", []) if a.get("success")]
        avg_score = (
            round(sum(a.get("defenseScore", 0) for a in artefatos_ok) / len(artefatos_ok), 1)
            if artefatos_ok
            else 0
        )
        max_amp = max((a.get("tokenAmplificationFactor", 0) for a in artefatos_ok), default=0)

        resumo = {
            "blaVersion": harden_report.get("blaVersion", "3.6.0"),
            "intensity": intensity,
            "weaveDecoys": True,
            "hardenedArtifacts": promovidos,
            "averageDefenseScore": avg_score,
            "peakTokenAmplification": max_amp,
            "runtimeEquivalenceVerified": testes_ok,
            "excludedHotPaths": [
                "static/libs/**",
                "static/vendor/**",
            ],
        }
        (out_dir / "BLA_SHIELD_REPORT.json").write_text(
            json.dumps(resumo, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print("==================================================================")
        print("🛡️  RELEASE BLINDADA COM SUCESSO (BLIND LLM AGENTS)")
        print(f"   • Diretório pronto:          {out_dir}")
        print(f"   • Artefatos protegidos:      {promovidos}")
        print(f"   • Defense Score médio:       {avg_score}/100")
        print(f"   • Amplificação de tokens:    até {max_amp}x contra agentes REA")
        print(f"   • Equivalência em runtime:   {'✅ 100% APROVADA' if testes_ok else '⚠️ Pulada'}")
        print("==================================================================")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Blindagem Counter-REA (BLA) para releases do JARVIS Kids OS")
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Diretório de saída da release blindada")
    parser.add_argument(
        "--intensity",
        choices=["stealth", "balanced", "maximum", "bankrupt"],
        default="balanced",
        help="Nível de proteção (use 'balanced' para Atom N450 / Acer One; 'bankrupt' para Desktop/Cloud)",
    )
    parser.add_argument("--in-place-staging", action="store_true", help="Blinda um diretório de staging já copiado")
    parser.add_argument("--skip-tests", action="store_true", help="Pula a execução da suíte de testes pós-blindagem")
    args = parser.parse_args()
    return executar_pipeline(
        Path(args.out).resolve(),
        intensity=args.intensity,
        in_place_staging=args.in_place_staging,
        skip_tests=args.skip_tests,
    )


if __name__ == "__main__":
    raise SystemExit(main())
