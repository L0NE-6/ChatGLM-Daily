<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ChatGLM Daily

**Automação em arquivo único para pontos de login diário, campanhas, tarefas diárias e tarefas de iniciante do Zhipu ChatGLM, com renovação de token e leitura de saldo.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> A documentação completa em chinês está em [../README.md](../README.md).

## ✨ Recursos principais

- Consulta `score_activity_open` antes de chamar `daily_login_score`.
- Distingue pontos recém-creditados, já recebidos, campanha inativa e estado desconhecido.
- Processa campanhas de pontos para membros e recompensas sazonais.
- Executa tarefas diárias em `click → complete`.
- Conclui tarefas de iniciante uma única vez e salva o estado localmente.
- Renova access tokens, persiste refresh tokens rotacionados e mantém a identidade do dispositivo por conta.
- Suporta notificações PushPlus, Bark, WeCom e DingTalk.

## 🚀 Configuração mínima

Na raiz do repositório:

```bash
python -m pip install -r requirements.txt
```

Leitura do cliente Windows:

```bash
python chatglm_login.py
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
```

Conta única:

```text
CHATGLM_TOKEN=ACCESS_TOKEN
CHATGLM_REFRESH_TOKEN=REFRESH_TOKEN
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Várias contas:

```text
CHATGLM_ACCOUNTS=
Principal|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
Secundária|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

Execução:

```bash
python chatglm_daily.py --query
python chatglm_daily.py
python chatglm_daily.py --only 1
python chatglm_daily.py --skip-newbie
python chatglm_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests cryptography
```

Defina `CHATGLM_ACCOUNTS` no painel e crie:

```text
10 8 * * * python3 chatglm_daily.py
```

`chatglm_state.json` guarda tokens rotacionados, ID do dispositivo e estado das tarefas de iniciante. Use um diretório gravável e persistente; `CHATGLM_STATE_FILE` permite alterar o caminho.

## ☁️ GitHub Actions

O workflow está em [../.github/workflows/daily.yml](../.github/workflows/daily.yml). A execução manual está ativa; o bloco de agendamento vem comentado.

| Secret | Obrigatório | Uso |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | Um dos dois | Credenciais de várias contas |
| `CHATGLM_TOKEN` | Um dos dois | Access token de uma conta |
| `CHATGLM_REFRESH_TOKEN` | Opcional | Refresh token de uma conta |
| `CHATGLM_DEVICE_ID` | Opcional | UUID do dispositivo |
| `CHATGLM_PROXY` | Opcional | Proxy |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | Opcional | Notificações |

Para ativar o agendamento, remova os comentários. O cron do GitHub usa UTC; `10 0 * * *` corresponde a 08:10 em Pequim. O Actions não preserva `chatglm_state.json`; atualize o Secret quando o refresh token mudar.

## 🔧 Variáveis principais

| Variável | Descrição |
| :--- | :--- |
| `CHATGLM_ACCOUNTS` | Várias contas: `nome\|access\|refresh\|device_id` |
| `CHATGLM_TOKEN` | Access token de uma conta |
| `CHATGLM_REFRESH_TOKEN` | Refresh token de uma conta |
| `CHATGLM_DEVICE_ID` | UUID do dispositivo, quando não puder ser lido do JWT |
| `CHATGLM_ACCOUNT_JSON` | JSON de contas como string |
| `CHATGLM_ACCOUNT_FILE` | Arquivo JSON de contas |
| `CHATGLM_STATE_FILE` | Estado de tokens e tarefas de iniciante |
| `CHATGLM_PROXY` | Proxy HTTP(S) / SOCKS |
| `CHATGLM_NO_NOTIFY` | `1` desativa notificações |

## 📊 Critério de sucesso

É necessário que ao menos uma conta não visitante conclua o fluxo de pontos de login com resultado confirmado de crédito ou recebimento anterior. Um valor de pontos ausente ou ilegível é marcado como não confirmado, em vez de ser tratado como sucesso.

## 🔒 Privacidade

- O projeto não coleta nem envia informações da conta.
- Os logs não exibem tokens completos.
- Não envie `chatglm_state.json`, `.env`, ID do dispositivo ou estado de login ao Git.
- Remova tokens e identificadores de conta antes de abrir uma issue.

## 🔗 Links

- [Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases)
- [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
