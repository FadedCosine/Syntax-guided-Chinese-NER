<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>CLUE 2020 &#x4E2D;&#x6587;&#x7EC6;&#x7C92;&#x5EA6;NER&#x4EFB;&#x52A1;</title>
        <style>
</style>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.10.2/dist/katex.min.css" integrity="sha384-yFRtMMDnQtDRO8rLpMIKrtPCD5jdktao2TV19YiZYWMDkUR5GQZR/NOVTdquEx1j" crossorigin="anonymous">
<link href="https://cdn.jsdelivr.net/npm/katex-copytex@latest/dist/katex-copytex.min.css" rel="stylesheet" type="text/css">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/markdown.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Microsoft/vscode/extensions/markdown-language-features/media/highlight.css">
<style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe WPC', 'Segoe UI', system-ui, 'Ubuntu', 'Droid Sans', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
        </style>
        <style>
.task-list-item { list-style-type: none; } .task-list-item-checkbox { margin-left: -20px; vertical-align: middle; }
</style>
        
        <script src="https://cdn.jsdelivr.net/npm/katex-copytex@latest/dist/katex-copytex.min.js"></script>
        
    </head>
    <body class="vscode-body vscode-light">
        <h1 id="clue-2020-中文细粒度ner任务">CLUE 2020 中文细粒度NER任务</h1>
<h2 id="概述">概述</h2>
<p>BERT等预训练模型虽然能够极大程度地提取出文本上下文信息，学习出通用语言表征，但却忽略了文本数据中的语言学特征，比如说句法。而句法信息通常展现了字词之间的语言依赖关系，这其中就包括了两个维度的信息，一是词汇的Lattice信息，二是字词之间的句法依赖信息。加上Lattice信息增强模型，以求改进中文NER的效果，在最近的研究中屡见不鲜，如<a href="https://arxiv.org/pdf/1805.02023v4.pdf">Lattice LSTM</a>、<a href="https://arxiv.org/pdf/2004.11795v2.pdf">FLAT</a>。同样作为增强模型理解能力的语言知识，目前却还没有研究深耕于句法信息改进中文NER的模型表现。</p>
<p>在本项目的工作中，受机器阅读理解领域的模型<a href="https://arxiv.org/abs/1908.05147">SG-Net</a>的启发，我们以一种Attention机制的方式，显式地利用句法依存树中句法信息，以求增强模型对于文本的理解能力，改进其在中文NER任务的表现。</p>
<p>如下样本及其文本的句法依存关系：</p>
<blockquote>
<p>{&quot;text&quot;: &quot;记者从东营市政府获悉，东营市目前对城市低收入住房困难家庭购买经济适用房实施货币化补贴政策。&quot;, &quot;label&quot;: {&quot;address&quot;: {&quot;东营市&quot;: [[11, 13]]}, &quot;government&quot;: {&quot;东营市政府&quot;: [[3, 7]]}, &quot;position&quot;: {&quot;记者&quot;: [[0, 1]]}}}</p>
</blockquote>
<table>
<thead>
<tr>
<th>From ID</th>
<th>From Lexicon</th>
<th>To Lexicon</th>
<th>To ID</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>记者</td>
<td>获悉</td>
<td>4</td>
</tr>
<tr>
<td>2</td>
<td>从</td>
<td>获悉</td>
<td>4</td>
</tr>
<tr>
<td>3</td>
<td>东营市政府</td>
<td>从</td>
<td>2</td>
</tr>
<tr>
<td>4</td>
<td>获悉</td>
<td>##核心##</td>
<td>0</td>
</tr>
<tr>
<td>5</td>
<td>，</td>
<td>获悉</td>
<td>4</td>
</tr>
<tr>
<td>6</td>
<td>东营市</td>
<td>实施</td>
<td>17</td>
</tr>
<tr>
<td>7</td>
<td>目前</td>
<td>实施</td>
<td>17</td>
</tr>
<tr>
<td>8</td>
<td>对</td>
<td>实施</td>
<td>17</td>
</tr>
<tr>
<td>9</td>
<td>城市</td>
<td>低收入</td>
<td>10</td>
</tr>
<tr>
<td>10</td>
<td>低收入</td>
<td>住房</td>
<td>11</td>
</tr>
<tr>
<td>11</td>
<td>住房</td>
<td>家庭</td>
<td>13</td>
</tr>
<tr>
<td>12</td>
<td>困难</td>
<td>家庭</td>
<td>13</td>
</tr>
<tr>
<td>13</td>
<td>家庭</td>
<td>对</td>
<td>8</td>
</tr>
<tr>
<td>14</td>
<td>购买</td>
<td>对</td>
<td>8</td>
</tr>
<tr>
<td>15</td>
<td>经济</td>
<td>适用房</td>
<td>16</td>
</tr>
<tr>
<td>16</td>
<td>适用房</td>
<td>购买</td>
<td>14</td>
</tr>
<tr>
<td>17</td>
<td>实施</td>
<td>获悉</td>
<td>4</td>
</tr>
<tr>
<td>18</td>
<td>货币化</td>
<td>政策</td>
<td>20</td>
</tr>
<tr>
<td>19</td>
<td>补贴</td>
<td>货币化</td>
<td>18</td>
</tr>
<tr>
<td>20</td>
<td>政策</td>
<td>实施</td>
<td>17</td>
</tr>
<tr>
<td>21</td>
<td>。</td>
<td>获悉</td>
<td>4</td>
</tr>
</tbody>
</table>
<p>如果要构建出一棵句法依存树，可以发现该句中的命名实体都作为完整的叶子结点出现在此句法依存树当中。因此，我们希望树中的每个结点去关注以此结点作为子树的树中所有叶子结点和此结点本身，这种Attention的机制既从句法中获益引导模型去关注可能的命名实体（命名实体常常作为句法依存树的叶子结点），又能使得模型获取Lattice的信息（句法依存分析的过程中就进行了分词，每个结点关注自己本身就获得了完整的Lattice信息）。具体地我们定义句法依存关注矩阵M如下：</p>
<p><span class="katex-display"><span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>M</mi><mo>=</mo><mrow><mo fence="true">{</mo><mtable rowspacing="0.24999999999999992em" columnalign="right left right" columnspacing="0em 1em"><mtr><mtd><mstyle scriptlevel="0" displaystyle="true"><mrow><mn>1</mn><mo separator="true">,</mo></mrow></mstyle></mtd><mtd><mstyle scriptlevel="0" displaystyle="true"><mrow></mrow></mstyle></mtd><mtd><mstyle scriptlevel="0" displaystyle="true"><mrow><mtext> if j</mtext><mo>∈</mo><mtext> Leaf(i) or j == i</mtext></mrow></mstyle></mtd></mtr><mtr><mtd><mstyle scriptlevel="0" displaystyle="true"><mrow><mn>0</mn><mo separator="true">,</mo></mrow></mstyle></mtd><mtd><mstyle scriptlevel="0" displaystyle="true"><mrow></mrow></mstyle></mtd><mtd><mstyle scriptlevel="0" displaystyle="true"><mrow><mi>o</mi><mi>t</mi><mi>h</mi><mi>e</mi><mi>r</mi><mi>w</mi><mi>i</mi><mi>s</mi><mi>e</mi></mrow></mstyle></mtd></mtr></mtable></mrow></mrow><annotation encoding="application/x-tex">M =\left\{
\begin{aligned}
1, &amp; &amp;  \text{ if j} \in \text{ Leaf(i) or j == i} \\
0, &amp;  &amp; otherwise  \\
\end{aligned}
\right.
</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.68333em;vertical-align:0em;"></span><span class="mord mathdefault" style="margin-right:0.10903em;">M</span><span class="mspace" style="margin-right:0.2777777777777778em;"></span><span class="mrel">=</span><span class="mspace" style="margin-right:0.2777777777777778em;"></span></span><span class="base"><span class="strut" style="height:3.00003em;vertical-align:-1.25003em;"></span><span class="minner"><span class="mopen delimcenter" style="top:0em;"><span class="delimsizing size4">{</span></span><span class="mord"><span class="mtable"><span class="col-align-r"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:1.7500000000000002em;"><span style="top:-3.91em;"><span class="pstrut" style="height:3em;"></span><span class="mord"><span class="mord">1</span><span class="mpunct">,</span></span></span><span style="top:-2.41em;"><span class="pstrut" style="height:3em;"></span><span class="mord"><span class="mord">0</span><span class="mpunct">,</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:1.2500000000000002em;"><span></span></span></span></span></span><span class="col-align-l"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:1.7500000000000002em;"><span style="top:-3.75em;"><span class="pstrut" style="height:2.84em;"></span><span class="mord"><span class="mord"></span></span></span><span style="top:-2.25em;"><span class="pstrut" style="height:2.84em;"></span><span class="mord"><span class="mord"></span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:1.2500000000000002em;"><span></span></span></span></span></span><span class="arraycolsep" style="width:1em;"></span><span class="col-align-r"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:1.7500000000000002em;"><span style="top:-3.91em;"><span class="pstrut" style="height:3em;"></span><span class="mord"><span class="mord text"><span class="mord"> if j</span></span><span class="mspace" style="margin-right:0.2777777777777778em;"></span><span class="mrel">∈</span><span class="mspace" style="margin-right:0.2777777777777778em;"></span><span class="mord text"><span class="mord"> Leaf(i) or j == i</span></span></span></span><span style="top:-2.41em;"><span class="pstrut" style="height:3em;"></span><span class="mord"><span class="mord mathdefault">o</span><span class="mord mathdefault">t</span><span class="mord mathdefault">h</span><span class="mord mathdefault">e</span><span class="mord mathdefault" style="margin-right:0.02778em;">r</span><span class="mord mathdefault" style="margin-right:0.02691em;">w</span><span class="mord mathdefault">i</span><span class="mord mathdefault">s</span><span class="mord mathdefault">e</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:1.2500000000000002em;"><span></span></span></span></span></span></span></span><span class="mclose nulldelimiter"></span></span></span></span></span></span></p>
<p>定义句法引导的multi-head self-attention操作如下：</p>
<p><span class="katex-display"><span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>A</mi><mi>i</mi></msub><mo>=</mo><mi>S</mi><mi>o</mi><mi>f</mi><mi>t</mi><mi>m</mi><mi>a</mi><mi>x</mi><mo stretchy="false">(</mo><mfrac><mrow><mi>M</mi><mo stretchy="false">(</mo><msub><mi>Q</mi><mi>i</mi></msub><msub><mi>K</mi><mi>i</mi></msub><mo stretchy="false">)</mo></mrow><msqrt><msub><mi>d</mi><mi>k</mi></msub></msqrt></mfrac><mo stretchy="false">)</mo></mrow><annotation encoding="application/x-tex">A_i = Softmax(\frac{M(Q_i K_i)}{\sqrt{d_k}})
</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault">A</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span><span class="mspace" style="margin-right:0.2777777777777778em;"></span><span class="mrel">=</span><span class="mspace" style="margin-right:0.2777777777777778em;"></span></span><span class="base"><span class="strut" style="height:2.357em;vertical-align:-0.93em;"></span><span class="mord mathdefault" style="margin-right:0.05764em;">S</span><span class="mord mathdefault">o</span><span class="mord mathdefault" style="margin-right:0.10764em;">f</span><span class="mord mathdefault">t</span><span class="mord mathdefault">m</span><span class="mord mathdefault">a</span><span class="mord mathdefault">x</span><span class="mopen">(</span><span class="mord"><span class="mopen nulldelimiter"></span><span class="mfrac"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:1.427em;"><span style="top:-2.25278em;"><span class="pstrut" style="height:3em;"></span><span class="mord"><span class="mord sqrt"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.85722em;"><span class="svg-align" style="top:-3em;"><span class="pstrut" style="height:3em;"></span><span class="mord" style="padding-left:0.833em;"><span class="mord"><span class="mord mathdefault">d</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.33610799999999996em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight" style="margin-right:0.03148em;">k</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span><span style="top:-2.81722em;"><span class="pstrut" style="height:3em;"></span><span class="hide-tail" style="min-width:0.853em;height:1.08em;"><svg width='400em' height='1.08em' viewBox='0 0 400000 1080' preserveAspectRatio='xMinYMin slice'><path d='M95,702
c-2.7,0,-7.17,-2.7,-13.5,-8c-5.8,-5.3,-9.5,-10,-9.5,-14
c0,-2,0.3,-3.3,1,-4c1.3,-2.7,23.83,-20.7,67.5,-54
c44.2,-33.3,65.8,-50.3,66.5,-51c1.3,-1.3,3,-2,5,-2c4.7,0,8.7,3.3,12,10
s173,378,173,378c0.7,0,35.3,-71,104,-213c68.7,-142,137.5,-285,206.5,-429
c69,-144,104.5,-217.7,106.5,-221
l0 -0
c5.3,-9.3,12,-14,20,-14
H400000v40H845.2724
s-225.272,467,-225.272,467s-235,486,-235,486c-2.7,4.7,-9,7,-19,7
c-6,0,-10,-1,-12,-3s-194,-422,-194,-422s-65,47,-65,47z
M834 80h400000v40h-400000z'/></svg></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.18278000000000005em;"><span></span></span></span></span></span></span></span><span style="top:-3.23em;"><span class="pstrut" style="height:3em;"></span><span class="frac-line" style="border-bottom-width:0.04em;"></span></span><span style="top:-3.677em;"><span class="pstrut" style="height:3em;"></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.10903em;">M</span><span class="mopen">(</span><span class="mord"><span class="mord mathdefault">Q</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.07153em;">K</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:-0.07153em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span><span class="mclose">)</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.93em;"><span></span></span></span></span></span><span class="mclose nulldelimiter"></span></span><span class="mclose">)</span></span></span></span></span></p>
<p>其中<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>K</mi><mi>i</mi></msub></mrow><annotation encoding="application/x-tex">K_i</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.07153em;">K</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:-0.07153em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>，<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mi>i</mi></msub></mrow><annotation encoding="application/x-tex">V_i</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.22222em;">V</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:-0.22222em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>，<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>Q</mi><mi>i</mi></msub></mrow><annotation encoding="application/x-tex">Q_i</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.8777699999999999em;vertical-align:-0.19444em;"></span><span class="mord"><span class="mord mathdefault">Q</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>分别表示对于第i个head，通过三个线性转换成的<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>n</mi><mo>×</mo><msub><mi>d</mi><mi>k</mi></msub></mrow><annotation encoding="application/x-tex">n\times d_k</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.66666em;vertical-align:-0.08333em;"></span><span class="mord mathdefault">n</span><span class="mspace" style="margin-right:0.2222222222222222em;"></span><span class="mbin">×</span><span class="mspace" style="margin-right:0.2222222222222222em;"></span></span><span class="base"><span class="strut" style="height:0.84444em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault">d</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.33610799999999996em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight" style="margin-right:0.03148em;">k</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>的key矩阵，<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>n</mi><mo>×</mo><msub><mi>d</mi><mi>v</mi></msub></mrow><annotation encoding="application/x-tex">n\times d_v</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.66666em;vertical-align:-0.08333em;"></span><span class="mord mathdefault">n</span><span class="mspace" style="margin-right:0.2222222222222222em;"></span><span class="mbin">×</span><span class="mspace" style="margin-right:0.2222222222222222em;"></span></span><span class="base"><span class="strut" style="height:0.84444em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault">d</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.151392em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight" style="margin-right:0.03588em;">v</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>的value矩阵和<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>n</mi><mo>×</mo><msub><mi>d</mi><mi>q</mi></msub></mrow><annotation encoding="application/x-tex">n\times d_q</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.66666em;vertical-align:-0.08333em;"></span><span class="mord mathdefault">n</span><span class="mspace" style="margin-right:0.2222222222222222em;"></span><span class="mbin">×</span><span class="mspace" style="margin-right:0.2222222222222222em;"></span></span><span class="base"><span class="strut" style="height:0.980548em;vertical-align:-0.286108em;"></span><span class="mord"><span class="mord mathdefault">d</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.15139200000000003em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight" style="margin-right:0.03588em;">q</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.286108em;"><span></span></span></span></span></span></span></span></span></span>的query矩阵。</p>
<p>而后通过将<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>A</mi><mi>i</mi></msub></mrow><annotation encoding="application/x-tex">A_i</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault">A</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>与<span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>V</mi><mi>i</mi></msub></mrow><annotation encoding="application/x-tex">V_i</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.22222em;">V</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:-0.22222em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span>相乘得到输入句子的句法引导词表征如下：</p>
<p><span class="katex-display"><span class="katex"><span class="katex-mathml"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>H</mi><mi>i</mi></msub><mo>=</mo><msub><mi>A</mi><mi>i</mi></msub><msub><mi>V</mi><mi>i</mi></msub></mrow><annotation encoding="application/x-tex">H_i = A_i V_i
</annotation></semantics></math></span><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.08125em;">H</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:-0.08125em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span><span class="mspace" style="margin-right:0.2777777777777778em;"></span><span class="mrel">=</span><span class="mspace" style="margin-right:0.2777777777777778em;"></span></span><span class="base"><span class="strut" style="height:0.83333em;vertical-align:-0.15em;"></span><span class="mord"><span class="mord mathdefault">A</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:0em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span><span class="mord"><span class="mord mathdefault" style="margin-right:0.22222em;">V</span><span class="msupsub"><span class="vlist-t vlist-t2"><span class="vlist-r"><span class="vlist" style="height:0.31166399999999994em;"><span style="top:-2.5500000000000003em;margin-left:-0.22222em;margin-right:0.05em;"><span class="pstrut" style="height:2.7em;"></span><span class="sizing reset-size6 size3 mtight"><span class="mord mathdefault mtight">i</span></span></span></span><span class="vlist-s">​</span></span><span class="vlist-r"><span class="vlist" style="height:0.15em;"><span></span></span></span></span></span></span></span></span></span></span></p>
<h3 id="数据介绍">数据介绍</h3>
<p>数据详细描述: <a href="https://www.cluebenchmarks.com/introduce.html">https://www.cluebenchmarks.com/introduce.html</a></p>
<h3 id="运行方式">运行方式</h3>
<ol>
<li>下载CLUE_NER数据集，运行以下命令：</li>
</ol>
<pre><code class="language-shell"><div>python tools/download_clue_data.py --data_dir=./datasets --tasks=cluener
</div></code></pre>
<ol start="2">
<li>从 <a href="https://huggingface.co/models">https://huggingface.co/models</a> 下载中文预训练模型，预训练模型文件格式，比如:</li>
</ol>
<pre><code class="language-text"><div>├── prev_trained_model　# 预训练模型
|  └── bert-base
|  | └── vocab.txt
|  | └── config.json
|  | └── pytorch_model.bin
</div></code></pre>
<ol start="3">
<li>训练：</li>
</ol>
<p>直接执行对应shell脚本，如：</p>
<pre><code class="language-shell"><div>sh scripts/run_ner_crf.sh
</div></code></pre>
<ol start="4">
<li>预测</li>
</ol>
<p>当前默认使用最后一个checkpoint模型作为预测模型，可通过--from_checkpoint指定checkpoint进行预测，或指定--from_all_checkpoints将依次load所有checkpoints进行预测。</p>
<h3 id="模型列表">模型列表</h3>
<p>model_type目前支持<strong>bert</strong>和<strong>albert</strong></p>
<p><strong>注意:</strong> bert ernie bert_wwm bert_wwwm_ext等模型只是权重不一样，而模型本身主体一样，因此参数model_type=bert其余同理。</p>
<h3 id="结果">结果</h3>
<p>bert_wwwm_ext在dev上为F1分数为0.8064</p>
<blockquote>
<p>代码改进基于 <a href="https://github.com/CLUEbenchmark/CLUENER2020">https://github.com/CLUEbenchmark/CLUENER2020</a></p>
</blockquote>

    </body>
    </html>