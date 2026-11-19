from pathlib import Path
import json
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
P=Path(__file__).resolve().parents[2];O=P/'code/outputs/rms_error_evaluation_20261120'
def read(name):return json.loads((O/name).read_text(encoding='utf-8'))
A=read('audit.json');G=read('group_diagnostics.json');F=read('official_reference_differences.json')
d=Document();s=d.sections[0];s.page_width=Cm(21);s.page_height=Cm(29.7);s.top_margin=s.bottom_margin=Cm(1.8);s.left_margin=s.right_margin=Cm(2)
for name,size in [('Normal',10.5),('Title',21),('Heading 1',16)]:
 st=d.styles[name];st.font.name='Calibri';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'微软雅黑');st.paragraph_format.space_after=Pt(7)
d.styles['Normal'].paragraph_format.line_spacing=1.1
for root in [d._element,d.styles.element]:
 for el in list(root.iter(qn('w:pBdr'))):el.getparent().remove(el)
ft=s.footer.paragraphs[0];ft.alignment=2;ft.add_run('CIVL 7023  |  误差评估  |  ');fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');ft._p.append(fld)
def p(x):d.add_paragraph(x)
def h(x):d.add_paragraph(x,'Heading 1')
def page(x):d.add_page_break();h(x)
def table(head,rows,widths):
 t=d.add_table(rows=1,cols=len(head));t.style='Table Grid';t.autofit=False
 for col,w in zip(t.columns,widths):col.width=Cm(w)
 for c,x in zip(t.rows[0].cells,head):c.text=str(x)
 for row in rows:
  for c,x in zip(t.add_row().cells,row):c.text=str(x)
 for row in t.rows:
  for c,w in zip(row.cells,widths):
   c.width=Cm(w)
   for a in c.paragraphs:
    a.paragraph_format.space_before=Pt(3);a.paragraph_format.space_after=Pt(4)
    for r in a.runs:r.font.size=Pt(9)
 d.add_paragraph().paragraph_format.space_after=Pt(0)
def f(x):return f'{x:.4f}' if abs(x)>=1e-5 else f'{x:.3g}'
d.add_paragraph('墙面 RMS 误差评估执行结果','Title')
p('2026年11月20日  |  按五步评估流程完成证据核查与误差统计')
p('本报告把已有实验按“确认可比性、准备参考、计算差异、稳定性检查、交付证据”五步逐项落实。本次读取并审核已有实际运行结果，新增明确的逐例误差表与按条件统计；没有重新扫描、训练或调参，也没有把已有实验冒充新实验。')
h('1 五步工作完成状态')
table(['步骤','本次完成内容','边界与状态'],[
 ['1 确认可比性','核对合成点集定义、单位、角点及官方说明','合成可确定；真实人工测区及口径待补'],
 ['2 准备参考答案','使用先验构造的完整墙 RMS；另保留可见墙点独立参考','未用待测程序输出作为真值'],
 ['3 计算并记录差异','335 例误差；44 个条件统计；4 项官方参考差异','真实差异不写成已确认的精度误差'],
 ['4 检查稳定性与失败','审核噪声、稀疏、遮挡、污染、截断及选区变化','保留全部不利结果；不以最小 RMS 挑参数'],
 ['5 保存结果与证据','输入、四点、参数、图及逐例记录均有路径','本报告和新统计表已生成；实墙严格验证未完成']],[2.7,7.4,6.9])
p('当前可以作出的结论：在正确、无噪声的选点条件下，程序通过已知真值数值检验；在若干受控污染和缺测条件下，它不能稳定恢复完整墙面的 RMS。不能把“程序正确计算所选点”扩大为“任意真实墙面都测得准确”。')
p('尚缺的关键资料不是另一套误差公式，而是人工参考究竟对应哪片墙、哪些点和哪种 RMS 定义。M26 已定位指定墙，但未知精确人工范围；M04 还缺官方定位图来源核验。因此本次能完成计算评估及有限条件对照，不能诚实宣称真实墙面的独立精度验证已完成。')

page('2 计算误差与分组结果')
p('每例新增三项显式指标：带符号误差 e = 预测 RMS − 参考 RMS；AE = |e|；相对误差 = AE / |参考 RMS| × 100%。335 例中有 9 例完整真值为零，相对误差为 null，CSV 对应空白并附 undefined_zero_reference 标记，不表示漏算或零误差。')
p('MAE = 平均 |e|，RMSE = √平均 e²，最大误差 = 最大 |e|。下面以完整无噪声墙的已知 RMS 为参考，展示不同压力类型的诊断汇总；不同参数条件的正式详细统计位于 condition_metrics.csv，共 44 行。没有计算混合所有条件的“总准确率”。')
names={'clean':'干净已知真值','noise':'法向噪声','sampling':'随机稀疏采样','occlusion':'中心遮挡','clutter':'前景污染','slab_clipping':'窄鼓包厚度截断','roi_change':'选区移动或缩小'}
table(['实验类型','例数','MAE mm','RMSE mm','最大 AE mm'],[
 [names[r['group']],r['n'],f(r['mae_mm']),f(r['rmse_mm']),f(r['max_ae_mm'])] for r in G],[4.6,1.5,3.4,3.4,4.1])
p('干净组 54/54 例满足预设 AE ≤ 10⁻⁶ mm，且目标点 Precision 与 Recall 均为 1。这个门限和极小误差用于检查数值算法，不能表示扫描设备具备相同精度。')
p('压力组的误差包含输入变化的影响。例如原墙真值为 1.8 mm，中心鼓包被遮挡后，剩余点 RMS 为 0.5361 mm，离完整墙差 1.2639 mm，但与可见点独立参考一致。选区移动或缩小也改变了统计对象，所以相对原完整墙的差异是范围敏感性，不是相同点集上的计算错误。')
p('相反，前景污染和厚度截断会使实际选中点偏离预期目标点集。前景约为墙点数 1% 时，真值 1.8 mm 的墙被算为约 3.4714 mm；窄鼓包真值 5 mm 在半厚度 50 mm 时被算为 2.2899 mm。这些失败不能从汇总中删除。')
p('暂定 AE ≤ 0.2 mm 仅是项目工作目标，非课程合格线或工程规范。不同种子是随机输入重复，不是独立实体墙；表中不能用于声称现场普遍精度或与论文不同房间直接排名。')

page('3 官方真实数据对照与稳定性')
table(['区域','预测 RMS mm','官方参考 mm','绝对差 mm','相对差'],[
 [r['room']+(' 主区域' if r['roi']=='main' else ' 扩展区域'),f(r['predicted_rms_mm']),f'{r["official_reference_mm"]:.1f}',f(r['abs_reference_difference_mm']),f'{r["relative_reference_difference_pct"]:.2f}%'] for r in F],[4.2,3.3,3.3,3.2,3])
p('四项均保持 same_roi_confirmed = false。官方人工值仍保留为外部参考；没有通过打开 gt-confirmed 开关伪造同区域确认。主/扩展区域属于同一房间的范围变体，不当作四面独立真值墙统计总体 MAE。')
table(['检查项目','M26 主区域','M04 候选主区域'],[
 ['半厚度 20/50/100 mm','RMS 均为 0.7048 mm','1.3380 / 3.7327 / 7.2916 mm'],
 ['四方向各平移 100 mm','0.6863 至 0.7208 mm','3.7011 至 3.7375 mm'],
 ['边长缩小至 90%','0.7101 mm','4.0639 mm'],
 ['当前解释','该上部区域相对稳定，但人工测区未知','对厚度强敏感，需核查选入点身份']],[5,6,6])
p('M26 稳定并不能证明它就是人工测区；M04 的大变化提示空间范围影响选点，但不能只凭距离给每个点确定“电线”或“真实鼓包”的身份。现有程序的 ok 状态也不等于无污染或测量达标。')
p('可回查证据：code/outputs/official_evaluation 中有四角 JSON、彩色墙面正视图、选区图、逐点距离、偏差图和厚度/位置扰动记录。原始官方点云未修改；本次重新检查了这些计算文件的哈希及参考差异。')
p('对真实墙面的正确表述是：“在自行确定的指定墙/候选墙区域计算得到上述 RMS，并给出与官方参考的差异；因人工范围与方法尚未对应，暂不将全部差异解释为算法误差。”')

page('4 交付文件与尚待解决的条件')
p(f'本次核查了 {A["hashed_evidence_files"]} 个已有证据文件的 SHA256，确认原生产代码未变；新增汇总与原始结果交叉核对一致。已有 335 份输入的完整重放记录显示复跑差为 0。本次未再次生成同一批模拟数据，也未反复运行不相关测试。')
table(['新文件','用途'],[
 ['synthetic_errors.csv / json','335 例显式误差、双参考、零参考状态、点集指标与输入证据路径'],
 ['condition_metrics.csv / json','44 个固定条件的偏差、MAE、RMSE、最大误差、成功/失败数'],
 ['group_diagnostics.csv / json','7 类实验的诊断统计；不代表统一现场精度'],
 ['official_reference_differences.csv / json','4 项真实区域的有限条件参考差异'],
 ['audit.json 与 manifest_sha256.json','证据核查结果、未完成条件与新文件哈希']],[7,10])
p('新文件均在 project/code/outputs/rms_error_evaluation_20261120。生成脚本为 code/scripts/finalize_rms_error_evaluation.py，拒绝覆盖已完成输出。它审核旧证据后计算误差，不改动预测结果。')
p('实际墙面严格验证需要补齐：①人工 1.0/1.8 mm 是整面墙还是局部区域，其三维边界或可定位测点；②参考采用哪些点、是否处理孔洞和构件、点权重如何确定；③是否同样使用最佳拟合平面的点到面 RMS；④参考测量方法和不确定度；⑤M04 的官方定位图。')
p('可以向资料提供者核实：“M26 的 1.0 mm、M04 的 1.8 mm 各对应哪片墙面区域？能否提供标记范围或点位、RMS 计算基准及人工测量方法？这些值是整墙统计还是局部测量？”这是待核实内容，本次没有替用户发送消息。')
p('如果原参考只代表整面墙，后续应按相同墙体范围取得点集，统一构件和孔洞处理后计算；若无法恢复口径，就保留当前有限对照，另按此前方案开展独立参考仪器实验，不能自行给真实墙编造真值。')
p('原详细设计、335 例实验说明和真实墙后续方案见 docs/Task1_RMS准确性评测设计与实验记录.docx。本报告是五步流程的执行核查与结果摘要。当前完成了能够依据现有证据完成的计算与稳定性评估；真实墙独立精度确认仍待补充参考条件。')
dest=P/'docs'/'Task1_RMS误差评估执行结果.docx';d.save(dest);print(dest)
