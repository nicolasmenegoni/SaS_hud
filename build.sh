#!/usr/bin/env bash
# Compila o plugin SaS_hud no Linux Mint (ou qualquer distro Debian-based).
# Uso:  ./build.sh            -> gera build/libs/SaS_hud-1.0.0.jar
#       ./build.sh --install  -> alem de compilar, copia o .jar para plugins/ (se existir)
set -euo pipefail

cd "$(dirname "$0")"

PLUGIN_NAME="SaS_hud"
VERSION="1.0.0"
API_VERSION="26.2"

BUILD_DIR="build"
CLASSES_DIR="$BUILD_DIR/classes"
GEN_SRC_DIR="$BUILD_DIR/java-gen"      # fora de src/, para nao poluir o repositorio
LIBS_DIR="$BUILD_DIR/libs"
JAR="$LIBS_DIR/${PLUGIN_NAME}-${VERSION}.jar"

# --- Dependencias (paper-api + transitivas), baixadas do repo da PaperMC ---
PAPER_BASE="https://repo.papermc.io/repository/maven-public"
DEPS=(
  "io/papermc/paper/paper-api/${API_VERSION}.build.134-stable/paper-api-${API_VERSION}.build.134-stable.jar"
  "net/kyori/adventure-api/5.2.0/adventure-api-5.2.0.jar"
  "net/kyori/adventure-key/5.2.0/adventure-key-5.2.0.jar"
  "net/kyori/adventure-text-minimessage/5.2.0/adventure-text-minimessage-5.2.0.jar"
  "org/joml/joml/1.10.8/joml-1.10.8.jar"
  "net/md-5/bungeecord-chat/1.20-R0.2/bungeecord-chat-1.20-R0.2.jar"
)
TMP_DEPS="/tmp/apidl"

echo "==> Verificando dependencias em $TMP_DEPS ..."
mkdir -p "$TMP_DEPS"
for path in "${DEPS[@]}"; do
  f="$TMP_DEPS/$(basename "$path")"
  if [ ! -s "$f" ]; then
    echo "    Baixando $(basename "$f") ..."
    curl -fsSL --retry 3 -o "$f" "$PAPER_BASE/$path"
  fi
done
TMP_DEPS="$(cd "$TMP_DEPS" && pwd)"
CP="$(printf "%s:" "$TMP_DEPS"/*.jar)"
CP="${CP%;}"

# --- JDK: o paper-api 26.x e compilado com class files major 69 (Java 25) -> exige JDK 25+ ---
REQUIRED_MAJOR=25
find_jdk() {
  # $1 = versao maior desejada; imprime JAVA_HOME se encontrar
  local want="$1" d
  for d in /usr/lib/jvm/java-"$want"-openjdk-amd64 /usr/lib/jvm/java-"$want"*-openjdk* \
           /opt/jdk"$want" /opt/jdk-"$want"* /usr/java/jdk-"$want"* "$HOME/.sdkman/candidates/java/$want"*; do
    [ -x "$d/bin/javac" ] && { echo "$d"; return 0; }
  done
  if command -v javac >/dev/null 2>&1; then
    local m; m="$(javac -version 2>&1 | awk '{print $2}' | cut -d. -f1)"
    [ "${m:-0}" -ge "$want" ] 2>/dev/null && { dirname "$(dirname "$(command -v javac)")"; return 0; }
  fi
  return 1
}
if ! JH="$(find_jdk "$REQUIRED_MAJOR")"; then
  # Tenta detectar a versao real exigida inspecionando o proprio paper-api baixado
  jar xf "$TMP_DEPS"/paper-api-*.jar org/bukkit/entity/Player.class --directory /tmp/apidl/probe 2>/dev/null \
    || (cd /tmp && jar xf "$TMP_DEPS"/paper-api-*.jar org/bukkit/entity/Player.class)
  if [ -f /tmp/org/bukkit/entity/Player.class ] || [ -f /tmp/apidl/probe/org/bukkit/entity/Player.class ]; then
    CM=$(od -An -t u1 -j 7 -N 1 /tmp/apidl/probe/org/bukkit/entity/Player.class 2>/dev/null \
        || od -An -t u1 -j 7 -N 1 /tmp/org/bukkit/entity/Player.class)
    case "${CM// /}" in 6[5-9]|7[0-9]*) REQUIRED_MAJOR=$(( ${CM// /} - 44 )) ;; esac
  fi
  DL="$HOME/.local/jdk$REQUIRED_MAJOR"
  if [ ! -x "$DL/bin/javac" ]; then
    echo "==> Baixando Eclipse Temurin JDK $REQUIRED_MAJOR (necessario p/ Paper $API_VERSION) para $DL ..."
    mkdir -p "$DL"
    curl -fsSL --retry 3 -o "/tmp/jdk$REQUIRED_MAJOR.tar.gz" \
      "https://api.adoptium.net/v3/binary/latest/$REQUIRED_MAJOR/ga/linux/x64/jdk/hotspot/normal/eclipse"
    tar xzf "/tmp/jdk$REQUIRED_MAJOR.tar.gz" -C "$DL" --strip-components=1
  fi
  JH="$DL"
fi
export JAVA_HOME="$JH"; export PATH="$JAVA_HOME/bin:$PATH"
echo "==> Usando $(javac -version 2>&1)"

# --- Geradores de assets (Python), se disponiveis ---
if command -v python3 >/dev/null 2>&1 && [ -d tools ]; then
  echo "==> Regenerando assets/texturas (tools/gen_bar_assets.py, gen_hud_pack.py) ..."
  python3 tools/gen_bar_assets.py || true
  python3 tools/gen_hud_pack.py   || true
fi

# --- Limpeza e compilacao ---
echo "==> Limpando $CLASSES_DIR ..."
rm -rf "$CLASSES_DIR" "$GEN_SRC_DIR"
mkdir -p "$CLASSES_DIR" "$GEN_SRC_DIR" "$LIBS_DIR"

# Garante que a fonte gerada referencia APIs existentes na versao usada.
has_api() {   # has_api <classe> <assinatura> -> sucesso se existir no paper-api usado
  javap -cp "$CP" -public "$1" 2>/dev/null | grep -qF "$2"
}
if ls src/main/java/com/nicolas/sas/hud/*.java >/dev/null 2>&1; then
  cp -r src/main/java/. "$GEN_SRC_DIR/"
  # Se a API de resource pack nao existir na versao do Paper usada, remove os trechos que a usam.
  if ! has_api org.bukkit.entity.Player "setResourcePack("; then
    for f in "$GEN_SRC_DIR"/com/nicolas/sas/hud/*.java; do
      sed -i '/setResourcePack\|ResourcePackStatus\|getResourcePackHash/d' "$f"
    done
    echo "    AVISO: API de resource pack ausente no paper-api usado — envio de pack desativado."
  fi
fi

echo "==> Compilando fontes ..."
find "$GEN_SRC_DIR" -name '*.java' > "$BUILD_DIR/sources.txt"
if [ -s "$BUILD_DIR/sources.txt" ]; then
  # paper-api 26.x usa class files Java 25 -> compilar com a MESMA versao do JDK (sem --release)
  javac -encoding UTF-8 -Xlint:-options -cp "$CP" \
        -d "$CLASSES_DIR" @"$BUILD_DIR/sources.txt"
else
  echo "ERRO: nenhuma fonte .java encontrada em src/main/java" >&2
  exit 1
fi

# --- Recursos (config.yml, plugin.yml, assets do resource pack) ---
echo "==> Copiando recursos ..."
cp -r src/main/resources/. "$CLASSES_DIR/"

# --- JAR ---
echo "==> Empacotando $JAR ..."
rm -f "$JAR"
MAIN_CLASS="$(grep -E '^main:' "$CLASSES_DIR/plugin.yml" | awk '{print $2}')"
[ -n "$MAIN_CLASS" ] || MAIN_CLASS="com.nicolas.sas.hud.HudPlugin"
ROOT="$PWD"; (cd "$CLASSES_DIR" && jar cfe "$ROOT/$JAR" "$MAIN_CLASS" .)

SIZE="$(du -h "$JAR" | cut -f1)"
echo "==> OK! Plugin compilado: $JAR ($SIZE)"

# --- Instalacao opcional ---
if [ "${1:-}" = "--install" ]; then
  DEST=""
  for d in ../server/plugins ../plugins plugins server/plugins; do
    [ -d "$d" ] && DEST="$d" && break
  done
  if [ -n "$DEST" ]; then
    cp -f "$JAR" "$DEST/"
    echo "==> Instalado em $DEST/"
  else
    echo "AVISO: pasta 'plugins' nao encontrada; copie $JAR manualmente." >&2
  fi
fi
