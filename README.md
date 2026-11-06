# NovaStar TB40 para Home Assistant

Integração comunitária em beta para controle local de brilho da NovaStar TB40. Ajusta de 1% a 100% em passos de 0,1 ponto percentual. Oferece curva solar e reenvio de brilho na partida com um relé configurado.

## Instalação pelo HACS

1. Em **HACS → menu → Repositórios personalizados**, cole a URL deste repositório e escolha **Integração**.
2. Baixe **NovaStar TB40** e reinicie o Home Assistant.
3. Em **Configurações → Dispositivos e serviços → Adicionar integração**, procure **NovaStar TB40**.

Para instalar manualmente, copie a pasta `custom_components/novastar_tb40` deste repositório para a pasta `custom_components` do Home Assistant e reinicie.

## Configuração

- **IPv4 local** da controladora, disponível no ViPlex Express ou no roteador.
- **Número de série**, disponível na etiqueta da TB40.
- **Usuário e senha local** da controladora. Comece pela senha do ViPlex. O formato esperado pelo campo AVON ainda precisa ser validado em outros firmwares.

O teste de rede verifica somente a porta TCP 16603. Ajuste **Brilho desejado** e confirme a mudança no painel físico. O Home Assistant exibe o último valor enviado. Use **Reconfigurar** para alterar IP ou senha.

## Automação opcional

Selecione o relé do painel nas opções para reaplicar o brilho após 5, 10, 20 e 30 segundos da partida. Ative a curva solar para usar a elevação do Sol como referência, com alvo de 100% a +5,5° e 8% a −3,5°. A integração cria uma entidade numérica de brilho. É possível vinculá-la a um helper de uma luz já existente.

## Compatibilidade e feedback

A versão 0.2.1 foi testada com uma TB40 e Home Assistant 2026.8. Outros firmwares ainda precisam de validação. Em um relato de problema, informe as versões e o comportamento observado. Omita IPs, números de série e credenciais.

Projeto comunitário. O logotipo identifica o equipamento e pertence à [NovaStar](https://www.novastar.tech/).
