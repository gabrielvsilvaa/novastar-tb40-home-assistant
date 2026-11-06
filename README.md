![Logotipo oficial da NovaStar](https://raw.githubusercontent.com/gabrielvsilvaa/novastar-tb40-home-assistant/main/custom_components/novastar_tb40/brand/logo.png)

# NovaStar TB40 para Home Assistant

Integração comunitária em beta para controle local de brilho da NovaStar TB40. Ajusta de 1% a 100% em passos de 0,1 ponto percentual. Oferece curva solar e reenvio de brilho na partida com um relé configurado.

## Instalação pelo HACS como repositório personalizado

**Pré-requisitos.** Tenha o HACS configurado, Home Assistant 2026.8.0 ou superior e acesso à rede local da TB40. Para o teste inicial, deixe a controladora ligada.

1. Abra **HACS** na barra lateral do Home Assistant.
2. Clique no menu **⋮** no canto superior direito da página principal do HACS e escolha **Repositórios personalizados** (*Custom repositories*).
3. No campo **Repositório** (*Repository*), cole a URL abaixo:

   ```text
   https://github.com/gabrielvsilvaa/novastar-tb40-home-assistant
   ```

4. Em **Tipo** (*Type*), escolha **Integração** (*Integration*) e clique em **Adicionar** (*Add*).
5. Feche a janela, pesquise **NovaStar TB40** na página principal do HACS e abra o resultado. Se ele não aparecer, limpe os filtros da busca e confirme que o repositório está na lista de personalizados.
6. Clique em **Baixar** (*Download*). A versão 0.2.1 foi publicada como pré-lançamento. Se ela não aparecer na lista de versões, abra o menu do repositório e habilite **Mostrar versões beta** (*Show beta versions*), se essa opção estiver disponível. Selecione a versão e confirme o download.
7. Reinicie o Home Assistant. Depois, abra **Configurações → Dispositivos e serviços → Adicionar integração**, pesquise **NovaStar TB40** e selecione-a.
8. Preencha os dados da TB40 descritos abaixo, conclua a configuração e teste o controle **Brilho desejado** no painel físico. O download pelo HACS instala os arquivos. O cadastro da controladora é feito nessa tela de integrações.

Para instalar manualmente, copie a pasta `custom_components/novastar_tb40` deste repositório para a pasta `custom_components` do Home Assistant e reinicie.

## Configuração

- **IPv4 local** da controladora, disponível no ViPlex Express ou no roteador.
- **Número de série**, disponível na etiqueta da TB40.
- **Usuário e senha local** da controladora. Comece pela senha do ViPlex. O formato esperado pelo campo AVON ainda precisa ser validado em outros firmwares.

O teste de rede verifica somente a porta TCP 16603. Ajuste **Brilho desejado** e confirme a mudança no painel físico. O Home Assistant exibe o último valor enviado. Use **Reconfigurar** para alterar IP ou senha.

## Relé opcional e automação com a Apple TV

O relé é opcional. Com o painel energizado, você pode ajustar o brilho pela integração sem configurar um relé. Para usar a curva solar e reaplicar o brilho na partida, selecione a entidade de interruptor que representa o comando de alimentação do painel.

**Exemplo com Apple TV.** Neste exemplo, o painel pode ser ligado e desligado de três formas: automaticamente pela automação da Apple TV, manualmente pelo app Casa via HomeKit Bridge ou diretamente pelo Home Assistant. Os três controles comandam o mesmo relé. O relé comanda uma contatora MG de 32 A, que liga e desliga a alimentação do painel. A marca e a corrente nominal são detalhes deste exemplo. A NovaStar TB40 acompanha o estado do relé no Home Assistant e reaplica o brilho na partida. A automação da Apple TV é configurada separadamente.

Selecione o relé do painel nas opções para reaplicar o brilho após 5, 10, 20 e 30 segundos da partida. Ative a curva solar para usar a elevação do Sol como referência, com alvo de 100% a +5,5° e 8% a −3,5°. A integração cria uma entidade numérica de brilho. É possível vinculá-la a um helper de uma luz já existente.

### Controle de brilho no HomeKit

Para ter um controle de brilho no app Casa, crie uma **luz de modelo (Template Light)** no Home Assistant ou reaproveite uma luz de modelo que já tenha suporte a brilho:

1. Configure as ações de ligar e desligar da luz para acionar o relé do painel. Use o estado desse relé como estado da luz.
2. Na ação de ajuste de brilho da luz, converta o nível de 0–255 para porcentagem e envie o valor à entidade **Brilho desejado** da NovaStar TB40 com a ação `number.set_value`. Use uma faixa de 1–100% enquanto a luz estiver ligada.
3. Use o brilho desejado da integração como fonte do nível da luz, convertendo a porcentagem de volta para 0–255. Se já usa um helper numérico para essa leitura, selecione-o em **Controle de brilho existente (opcional)** nas opções da TB40.
4. Exponha a **entidade de luz** pelo **HomeKit Bridge** e use o controle de brilho no app Casa.

O relé fornece o controle de energia. A luz de modelo combina esse controle com o ajuste de brilho da TB40.

## Compatibilidade e feedback

A versão 0.2.1 foi testada com uma TB40 e Home Assistant 2026.8. Outros firmwares ainda precisam de validação. Em um relato de problema, informe as versões e o comportamento observado. Omita IPs, números de série e credenciais.

Projeto comunitário. O logotipo identifica o equipamento e pertence à [NovaStar](https://www.novastar.tech/).
