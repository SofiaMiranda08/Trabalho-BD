#!/bin/bash
# Configura o painel Olho na Cota em um servidor AWS EC2 (Ubuntu).
# Uso (dentro da pasta do projeto no servidor):  bash deploy_aws.sh
set -e
PASTA="$(cd "$(dirname "$0")" && pwd)"
USUARIO="$(whoami)"

echo ">> Instalando Python..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv

echo ">> Instalando bibliotecas do projeto..."
python3 -m venv "$PASTA/venv"
"$PASTA/venv/bin/pip" install --upgrade pip
"$PASTA/venv/bin/pip" install -r "$PASTA/requirements.txt"

echo ">> Criando servico para o painel ficar sempre no ar..."
sudo tee /etc/systemd/system/olhonacota.service > /dev/null <<SVC
[Unit]
Description=Painel Olho na Cota (Streamlit)
After=network.target

[Service]
User=$USUARIO
WorkingDirectory=$PASTA
ExecStart=$PASTA/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
SVC

sudo systemctl daemon-reload
sudo systemctl enable --now olhonacota
sleep 3
IP=$(curl -s http://checkip.amazonaws.com || echo "SEU_IP_PUBLICO")
echo ""
echo "=============================================="
echo " Painel no ar em:  http://$IP:8501"
echo "=============================================="
