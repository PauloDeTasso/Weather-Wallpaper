<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=13&pause=1000&color=58A6FF&center=true&vCenter=true&width=500&lines=Weather+Dynamic+Wallpaper+App;Windows+11+%7C+Python+%7C+CustomTkinter;Real-time+climate+%C3%97+Visual+experience" alt="Typing SVG" />

# 🌤 Weather Dynamic Wallpaper

> **Seu desktop respira o clima real — em tempo real.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1f6feb?style=flat-square)](https://github.com/TomSchimansky/CustomTkinter)
[![API](https://img.shields.io/badge/API-Open--Meteo-00b4d8?style=flat-square)](https://open-meteo.com)
[![Windows](https://img.shields.io/badge/Platform-Windows%2011-0078D4?style=flat-square&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](#)
[![Status](https://img.shields.io/badge/Status-Active-3fb950?style=flat-square)](#)

</div>

---

## 📌 Sobre o Projeto

O **Weather Dynamic Wallpaper** é uma aplicação desktop para Windows 11 que monitora as condições climáticas em tempo real e troca automaticamente o papel de parede do sistema de acordo com o **clima atual** e o **período do dia**.

A ideia nasce de uma percepção simples: a experiência visual do seu desktop pode ser tão dinâmica quanto o mundo lá fora. Uma manhã chuvosa merece um fundo diferente de uma tarde ensolarada — e este sistema faz exatamente isso, de forma autônoma, elegante e totalmente personalizável.

> Desenvolvido como projeto de vitrine por **Paulo de Tasso**, estudante do 7º período de Engenharia de Software na **Estácio — Rio de Janeiro**, demonstrando integração de APIs, arquitetura modular, programação concorrente e desenvolvimento de interfaces gráficas modernas com Python.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🌐 **API Open-Meteo** | Dados climáticos em tempo real, gratuita, sem API key |
| 🕐 **6 Períodos do Dia** | Amanhecer, Manhã, Tarde, Anoitecer, Noite, Madrugada |
| 🌦️ **11 Condições Climáticas** | Limpo, Nublado, Chuva, Tempestade, Pós-chuva, Neblina, Neve, Vento, Frio, Calor |
| 🖼️ **66 Slots de Imagem** | Um para cada combinação condição × período |
| 📂 **Seleção Individual** | Botão próprio por imagem — sem renomear arquivos |
| 📊 **Painel de Dados** | Todos os dados da API exibidos de forma legível e formatada |
| 🌈 **Pós-Chuva Inteligente** | Detecta automaticamente a transição chuva → céu aberto |
| ⏱️ **Contador Regressivo** | Mostra o tempo até a próxima atualização em tempo real |
| 📍 **Geolocalização** | Detecta sua localização automaticamente via IP |
| 🖥️ **System Tray** | Roda em segundo plano com ícone na bandeja do Windows |
| 🚀 **Iniciar com Windows** | Integração com o registro do sistema operacional |
| 🔄 **Retry Automático** | Resiliência a falhas de rede com cache do último wallpaper |

---

## 🕐 Períodos do Dia

```
🌅 Amanhecer   05:00 – 07:00
🌄 Manhã       07:00 – 12:00
☀️  Tarde       12:00 – 18:00
🌇 Anoitecer   18:00 – 20:00
🌃 Noite       20:00 – 00:00
🌌 Madrugada   00:00 – 05:00
```

---

## 🌦️ Condições Climáticas

```
☀️  Céu Limpo           — WMO code 0–1
⛅  Parcialmente Nublado — WMO code 2
☁️  Nublado              — WMO code 3
🌧️  Chuva                — WMO code 51–67, 80–82
⛈️  Tempestade           — WMO code 95–99
🌈  Pós-Chuva            — Transição chuva → limpo (detectada automaticamente)
🌫️  Neblina              — WMO code 45–48
❄️  Neve                 — WMO code 71–77, 85–86
💨  Vento Forte          — Vento > 25 km/h em céu aberto
🧊  Frio                 — Temperatura ≤ 10°C em céu aberto
🔥  Calor Extremo        — Temperatura ≥ 35°C em céu aberto
```

---

## 🏗️ Arquitetura

```
weather-wallpaper-app/
│
├── 📄 main.py                     ← Ponto de entrada
├── 📄 config.json                 ← Configurações persistentes
├── 📄 WeatherWallpaper.spec       ← Configuração de build (PyInstaller)
│
├── 📁 core/
│   ├── weather_api.py             ← Integração Open-Meteo (retry, cache)
│   ├── weather_mapper.py          ← Lógica de mapeamento clima → wallpaper
│   ├── wallpaper_controller.py    ← API nativa Windows (SystemParametersInfoW)
│   └── scheduler.py               ← Loop concorrente com threading
│
├── 📁 ui/
│   ├── dashboard.py               ← Interface gráfica (CustomTkinter)
│   └── tray.py                    ← Ícone na bandeja do sistema
│
├── 📁 utils/
│   ├── config_manager.py          ← Leitura/escrita de configurações JSON
│   ├── location_helper.py         ← Geolocalização por IP
│   └── startup_manager.py         ← Registro do Windows (startup)
│
└── 📁 assets/
    └── (suas imagens aqui)
```

---

## 📊 Dados Exibidos da API

O painel de clima apresenta todos os campos do JSON retornado pela Open-Meteo de forma legível e organizada:

| Campo JSON | Como é exibido |
|---|---|
| `weathercode` | Código WMO + descrição oficial em PT-BR |
| `temperature` | Temperatura atual + Sensação térmica calculada |
| `windspeed` | Velocidade em km/h + Intensidade (Calmo / Fraco / Moderado / Forte…) |
| `winddirection` | Graus + Rosa dos ventos (Norte, Nordeste, Sul, Sudoeste…) |
| `is_day` | ☀️ Dia ou 🌙 Noite |
| `time` | Horário exato da última leitura |
| *(calculado)* | Período do dia baseado no horário local do sistema |
| *(calculado)* | Chave do wallpaper ativo no momento |

---

## ⚙️ Instalação e Build

**Pré-requisitos:** Python 3.10+ no Windows 11

### Rodar em modo desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/weather-wallpaper-app.git
cd weather-wallpaper-app

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py
```

### Gerar o executável `.exe`

```bash
# Instale o PyInstaller
pip install pyinstaller

# Gere o .exe com um clique (sem console, tudo embutido)
pyinstaller WeatherWallpaper.spec
```

O executável final fica em:

```
dist/
└── WeatherWallpaper.exe   ← clique duplo, abre direto
```

> As configurações do usuário são salvas automaticamente em  
> `%APPDATA%\WeatherWallpaper\config.json`

**Dependências:**

```
customtkinter >= 5.2.0
Pillow        >= 10.0.0
requests      >= 2.31.0
pystray       >= 0.19.0
```

---

## 🖼️ Como Usar

1. Execute `WeatherWallpaper.exe` (ou `python main.py` em modo dev)
2. Na aba **⚙️ Configurações**, insira sua latitude e longitude  
   *(ou clique em "📡 Detectar automaticamente")*
3. Na aba **🖼️ Imagens por Condição**, clique em **📂 Escolher** em cada linha para mapear suas fotos
4. Clique em **▶ Iniciar** — o sistema começa a monitorar e trocar o wallpaper automaticamente
5. O app minimiza para a bandeja do sistema e continua rodando em segundo plano

---

## 🔬 Conceitos Técnicos Demonstrados

- **Integração com API REST** — consumo, parsing e tratamento de erros com retry automático
- **Programação Concorrente** — threads independentes para scheduler, tray e UI (thread-safety via `after()`)
- **Arquitetura em Camadas** — separação clara entre `core`, `ui` e `utils`
- **Persistência de Estado** — configurações salvas em JSON com merge inteligente de defaults
- **Interoperabilidade com SO** — chamada direta à Win32 API via `ctypes` sem dependências externas
- **Empacotamento com PyInstaller** — `.spec` customizado, `resource_path()`, dados em `%APPDATA%`
- **Design de Interface Moderno** — dark mode com CustomTkinter, badges coloridos, tabview, scrollable frames
- **Resiliência** — retry automático, fallback em cascata entre condições, cache do último wallpaper válido

---

## 👨‍💻 Autor

<div align="center">

### Paulo de Tasso
**Engenharia de Software — 7º Período**  
Estácio · Rio de Janeiro, RJ — Brasil

*"Transformando dados climáticos em experiências visuais."*

[![GitHub](https://img.shields.io/badge/GitHub-@seu--usuario-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/seu-usuario)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Paulo%20de%20Tasso-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/seu-perfil)

</div>

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja [`LICENSE`](LICENSE) para mais informações.

---

<div align="center">

**⭐ Se este projeto foi útil, deixe uma estrela — ajuda muito!**

*Feito com ☕ e Python no Rio de Janeiro*

</div>
