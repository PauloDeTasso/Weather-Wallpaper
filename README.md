# 🌤 Weather Dynamic Wallpaper App

Aplicativo desktop para Windows 10/11 que altera automaticamente o papel de parede com base no clima real.

---

## 📦 Requisitos

- Windows 11 (64-bit)
- Python 3.10+

---

## 🚀 Instalação

### 1. Clone ou extraia o projeto

```
weather-wallpaper-app/
```

### 2. Instale as dependências

```bash
pip install customtkinter pillow requests pystray
```

### 3. Execute

```bash
python main.py
```

---

## 🖼️ Adicionando Imagens

Coloque suas imagens na pasta `assets/` com os nomes:

| Condição | Arquivo (dia) | Arquivo (noite) |
|---|---|---|
| Céu limpo | `clear_day.jpg` | `clear_night.jpg` |
| Parcialmente nublado | `partly_cloudy_day.jpg` | `partly_cloudy_night.jpg` |
| Nublado | `cloudy_day.jpg` | `cloudy_night.jpg` |
| Neblina | `fog_day.jpg` | `fog_night.jpg` |
| Chuva | `rain_day.jpg` | `rain_night.jpg` |
| Neve | `snow_day.jpg` | `snow_night.jpg` |
| Pancadas | `showers_day.jpg` | `showers_night.jpg` |
| Tempestade | `storm_day.jpg` | `storm_night.jpg` |
| Vento forte (>25 km/h) | `windy_day.jpg` | `windy_night.jpg` |
| Calor extremo (≥32°C) | `hot_day.jpg` | `hot_night.jpg` |
| Frio (≤15°C) | `cold_day.jpg` | `cold_night.jpg` |

**Ou use o botão "Selecionar Pasta" na interface para mapear automaticamente!**

---

## ⚙️ Configuração

Edite `config.json` ou use a interface gráfica:

- **latitude / longitude** → suas coordenadas
- **update_interval_minutes** → frequência de atualização
- **auto_mode** → ativar/desativar troca automática
- **wallpaper_map** → mapeamento completo clima → imagem

---

## 🔄 Funcionalidades

- ✅ Clima em tempo real via Open-Meteo (gratuito, sem API key)
- ✅ Diferenciação dia/noite automática
- ✅ Regras avançadas: vento, calor extremo, frio
- ✅ Interface moderna estilo Windows 11 (CustomTkinter)
- ✅ Ícone na bandeja do sistema
- ✅ Retry automático em falhas de API
- ✅ Cache da última imagem válida
- ✅ Detecção automática de localização por IP
- ✅ Iniciar com Windows (via registro)
- ✅ Preview do wallpaper atual
- ✅ Seleção de pasta com auto-mapeamento

---

## 🔐 API usada

[Open-Meteo](https://open-meteo.com/) — gratuita, sem cadastro, sem API key.

---

## 📁 Estrutura

```
weather-wallpaper-app/
├── main.py
├── config.json
├── README.md
├── requirements.txt
├── core/
│   ├── weather_api.py
│   ├── wallpaper_controller.py
│   ├── weather_mapper.py
│   └── scheduler.py
├── ui/
│   ├── dashboard.py
│   └── tray.py
├── utils/
│   ├── config_manager.py
│   ├── location_helper.py
│   └── startup_manager.py
└── assets/
    └── (suas imagens aqui)
```


# 🌦️ Weather Dynamic Wallpaper

<p align="center">
	<img src="https://img.shields.io/badge/Windows-11-0078D6?style=for-the-badge&logo=windows&logoColor=white">
	<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white">
	<img src="https://img.shields.io/badge/Open--Meteo-API-FFB000?style=for-the-badge">
	<img src="https://img.shields.io/badge/Status-Development-00C853?style=for-the-badge">
</p>

---

<p align="center">
	<b>Transforme seu desktop em um ambiente vivo conectado ao clima em tempo real.</b>
</p>

<p align="center">
	O aplicativo altera automaticamente o wallpaper do Windows 11 com base nas condições climáticas atuais da sua cidade.
</p>

---

# ✨ Preview

* ☀️ Céu limpo → wallpapers ensolarados
* 🌧️ Chuva → wallpapers chuvosos
* ⛈️ Tempestade → wallpapers dinâmicos
* 🌙 Dia e noite automáticos
* 💨 Variações baseadas em vento e temperatura
* 🪟 Integração nativa com Windows 11

---

# 🚀 Recursos

## 🌦️ Clima em tempo real

Integração com a API Open-Meteo para atualização automática das condições climáticas.

## 🖼️ Wallpaper dinâmico

Troca automática do papel de parede baseada em:

* clima
* horário
* temperatura
* vento
* dia/noite

## 🎨 Personalização completa

Configure wallpapers diferentes para:

* céu limpo
* chuva
* tempestade
* neblina
* noite
* calor
* frio
* vento forte

## 📍 Localização personalizada

Escolha:

* latitude
* longitude
* localização automática opcional

## 🪟 Interface moderna

Painel moderno inspirado no visual do Windows 11.

## ⚡ Leve e eficiente

* baixo consumo de RAM
* baixo uso de CPU
* execução em background

## 🔄 Atualização automática

Defina:

* 5 min
* 10 min
* 15 min
* 30 min
* personalizado

---

# 🧠 Como funciona

O aplicativo consulta periodicamente:

```txt
https://api.open-meteo.com/v1/forecast
```

Exemplo de resposta:

```json
{
  "current_weather": {
    "temperature": 22.7,
    "windspeed": 20.0,
    "winddirection": 131,
    "is_day": 1,
    "weathercode": 2
  }
}
```

O sistema interpreta:

* `weathercode`
* `is_day`
* `temperature`
* `windspeed`

E define automaticamente o wallpaper ideal.

---

# 🌤️ Mapeamento climático

| Código | Clima                |
| ------ | -------------------- |
| 0      | Céu limpo            |
| 1      | Quase limpo          |
| 2      | Parcialmente nublado |
| 3      | Nublado              |
| 45-48  | Neblina              |
| 51-67  | Chuva                |
| 71-77  | Neve                 |
| 80-82  | Pancadas de chuva    |
| 95+    | Tempestade           |

---

# 🖥️ Tecnologias

* Python 3.10+
* CustomTkinter
* Requests
* Pillow
* Pystray
* Win32 API
* Open-Meteo API

---

# 📂 Estrutura do Projeto

```txt
weather-wallpaper-app/
│
├── main.py
├── config.json
│
├── core/
│   ├── weather_api.py
│   ├── wallpaper_controller.py
│   ├── weather_mapper.py
│   ├── scheduler.py
│
├── ui/
│   ├── dashboard.py
│   ├── tray.py
│
├── assets/
│   ├── clear.jpg
│   ├── rain.jpg
│   ├── storm.jpg
│
└── utils/
    ├── location_helper.py
```

---

# ⚙️ Instalação

## 📦 Clonar projeto

```bash
git clone SEU_REPOSITORIO
```

---

## 🐍 Criar ambiente virtual

```bash
python -m venv venv
```

---

## ▶️ Ativar ambiente virtual

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### CMD

```cmd
venv\Scripts\activate.bat
```

---

## 📥 Instalar dependências

```bash
pip install -r requirements.txt
```

---

# ▶️ Executar

```bash
python main.py
```

---

# 📦 Gerar executável Windows (.exe)

```bash
pyinstaller --onefile --noconsole --icon=app.ico main.py
```

Executável final:

```txt
dist/main.exe
```

---

# 🎛️ Funcionalidades planejadas

* [ ] Sistema de temas
* [ ] Wallpapers animados
* [ ] Transições suaves
* [ ] Múltiplos monitores
* [ ] Integração com Steam Wallpaper Engine
* [ ] Auto updater
* [ ] Widget climático
* [ ] Modo gaming
* [ ] IA para seleção automática de wallpapers

---

# 🔐 Segurança

* validação de entrada
* tratamento de falhas da API
* prevenção de loops excessivos
* cache de último wallpaper válido
* proteção contra troca repetitiva desnecessária

---

# 🪟 Compatibilidade

| Sistema    | Suporte   |
| ---------- | --------- |
| Windows 11 | ✅         |
| Windows 10 | ✅         |
| Linux      | ⚠️ Futuro |
| macOS      | ⚠️ Futuro |

---

# 🤝 Contribuição

Contribuições são bem-vindas.

Você pode ajudar com:

* melhorias visuais
* novos temas
* otimização
* integração multi-monitor
* novas engines de wallpaper

---

# 📜 Licença

Projeto distribuído sob licença MIT.

---

# 🌌 Objetivo

Criar uma experiência desktop viva, elegante e conectada ao clima do mundo real.

---

<p align="center">
	Desenvolvido para Windows 11 ☁️
</p>
