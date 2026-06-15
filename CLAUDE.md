# qwen3tts-server

API simples no padrão OpenAI para utilizar o Qwen3 TTS como serviço em container.

## Visão geral

Servidor HTTP compatível com a API `/v1/audio/speech` da OpenAI, permitindo integração com ferramentas e clientes existentes. Construído com FastAPI e empacotado em Docker.

## Requisitos de hardware

- **CPU**: deve rodar sem GPU
- **GPU**: deve suportar NVIDIA RTX (CUDA); a execução com GPU é o caminho principal de performance

## Estrutura de diretórios

```
src/          # código-fonte da aplicação
src/tests/    # testes unitários e de integração
```

## Agentes disponíveis

Este projeto utiliza três agentes especializados que **devem trabalhar em conjunto** para qualquer plano, implementação de nova feature ou correção de bug:

| Agente | Papel |
|--------|-------|
| `arquiteto` | Desenha a arquitetura antes de qualquer implementação |
| `programador-tester` | Escreve os testes antes do código (TDD) |
| `programador` | Implementa o código de produção |

### Fluxo obrigatório

1. **arquiteto** define a solução arquitetural (nunca escreve código)
2. **programador-tester** escreve os testes com base na arquitetura definida
3. **programador** implementa o código que faz os testes passarem

## Metodologia de desenvolvimento

> **Regra absoluta: TDD obrigatório em toda implementação.**

- **NUNCA escreva código de produção sem antes criar os testes unitários automatizados correspondentes.**
- O ciclo obrigatório é: **red → green → refactor**
  1. Escreva o teste — ele deve falhar (red)
  2. Implemente o mínimo de código para o teste passar (green)
  3. Refatore mantendo todos os testes verdes
- Ao final de qualquer implementação, **todos os testes devem estar passando**. Corrija o que for necessário até atingir esse estado antes de considerar a tarefa concluída.

## Convenções

- Código de produção em `src/`
- Testes em `src/tests/`
- Sem overdesign: prefira soluções simples e duráveis
- Sem comentários óbvios; comente apenas o *porquê* quando não for evidente
- **NUNCA faça commit no git automaticamente sem antes perguntar ao usuário**
