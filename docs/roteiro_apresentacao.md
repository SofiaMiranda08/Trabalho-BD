# Roteiro de apresentação — Olho na Cota

## Frase-resumo
"O Olho na Cota usa engenharia de dados para transformar R$ 215 milhões em gastos públicos em informação clara, ajudando a sociedade a fiscalizar o uso do dinheiro público."

## Fala geral
1. **Abertura:** "Nosso projeto se chama Olho na Cota. Ele usa engenharia de dados para mostrar como os deputados federais usam a Cota Parlamentar."
2. **Problema:** "A Câmara divulga todos esses gastos, mas num arquivo com 171 mil linhas. O dado é público, mas na prática ninguém consegue ler."
3. **Solução:** "Transformamos esse arquivo num painel com gráficos simples, que qualquer cidadão entende."
4. **Como fizemos:** "Seguimos a Arquitetura Medalhão: coletamos o dado oficial, limpamos com Python, organizamos num banco MySQL e mostramos tudo no painel."
5. **Descobertas:** "Em 2025, foram R$ 215 milhões. Quase metade foi para divulgação do mandato. Identificamos mais de 31 mil gastos fora do padrão."
6. **Impacto:** "O eleitor pode consultar o próprio deputado, e jornalistas e órgãos de controle sabem onde investigar primeiro."
7. **Fechamento:** "O dinheiro é público, e a informação também precisa ser acessível. Obrigada!"

## Fala por tela
- **Início:** problema, R$ 215 milhões, 171 mil linhas. Dado público só vira transparência quando a população entende.
- **Visão geral:** gasto estável, em torno de R$ 18 milhões por mês. O cidadão acompanha se os gastos sobem.
- **Categorias:** quase metade vai para divulgação do mandato. Abre o debate sobre o melhor uso do dinheiro.
- **Deputados:** ranking e busca. O eleitor fiscaliza o próprio representante.
- **Estados e partidos:** mapa de calor da média por deputado (maior: AC; menor: AP). Partidos só com 5+ deputados, para um único deputado não distorcer a média.
- **Fornecedores:** quem mais recebeu. Permite verificar concentração.
- **Alertas:** regra IQR, mais de 31 mil gastos sinalizados e nenhum apagado. Mostra onde olhar primeiro.
- **Sobre o projeto:** Bronze, Prata, Ouro e o esquema estrela (fato + 3 dimensões).

## Perguntas prováveis
**O que é a CEAP?** Verba mensal para despesas do mandato (passagens, combustível, escritório, divulgação). Não é salário, é reembolso mediante nota fiscal.

**Todo deputado recebe o mesmo valor?** Não. O limite muda conforme o estado. Estados mais longe de Brasília têm limite maior por causa das viagens.

**Quem fiscaliza?** A Câmara confere as notas e pode cortar valores (glosa, mais de R$ 1 milhão em 2025). O TCU também fiscaliza, e a sociedade acompanha pelos dados abertos (Lei de Acesso à Informação).

**Gasto alto é irregular?** Não necessariamente. Mostra onde olhar com mais atenção, não prova nada.

**O que é outlier?** Valor muito diferente da maioria. Usamos a regra estatística IQR: acima de Q3 + 1,5 × IQR.

**Por que não apagar os outliers?** Podem ser gastos reais, e são os que mais interessam à fiscalização.

**Limitações?** Meses finais podem estar incompletos (notas chegam com atraso), registros de lideranças ficaram fora dos rankings, e o painel mostra quanto foi gasto, não se o gasto foi certo.

**Como ajuda no dia a dia?** Ajuda a votar e cobrar com base em fatos: consultar o deputado antes da eleição, comparar estados e partidos e questionar gastos estranhos. O painel não diz em quem votar.

**Se não souber:** "Boa pergunta! Isso não entrou no escopo, mas seria um ótimo próximo passo."
