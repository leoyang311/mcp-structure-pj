"""
升级版内容生成提示词 - 基于CASE框架和信息密度要求
彻底解决空话连篇和信息密度低的问题
"""

from typing import Dict, Any, List
from ..models import Platform
from ..engines.deep_research_engine import StructuredResearch, InformationDensityCalculator

class CASEFrameworkPrompts:
    """CASE框架提示词生成器"""
    
    @staticmethod
    def get_case_enforcement_prompt() -> str:
        """CASE框架强制执行基础提示词"""
        return """
# CASE框架强制执行 - 零容忍空话政策

你必须严格遵守CASE框架，任何违反都将导致内容被拒绝。

## 绝对禁止的空话表达
❌ "据了解" "有消息称" "业内人士表示" "分析认为"
❌ "大约" "左右" "相关" "一定程度上" "总的来说"  
❌ "值得注意的是" "引起关注" "备受期待" "广泛讨论"

## CASE框架强制要求

### C - Concrete Data (具体数据) - 强制执行
✅ 必须包含精确数字：不说"巨额投资"，说"158.6亿元投资"
✅ 必须包含准确时间：不说"近期"，说"2024年11月28日"  
✅ 必须包含具体名称：不说"某科技公司"，说"小米集团(01810.HK)"
✅ 必须包含准确地点：不说"海外"，说"澳大利亚墨尔本市"

### A - Actual Examples (真实案例) - 强制执行  
✅ 每个观点必须有具体案例支撑
✅ 案例必须包含完整的5W1H信息
✅ 必须有可验证的细节描述
✅ 避免"比如说"，直接给出具体案例

### S - Specific Details (具体细节) - 强制执行
✅ 技术参数：不说"高性能"，说"最大功率295kW，峰值扭矩838N·m"
✅ 财务数据：不说"营收增长"，说"营收同比增长23.4%至518.5亿元"
✅ 人员信息：不说"高管团队"，说"CEO雷军，CFO林世伟，总裁王翔"  
✅ 过程细节：不说"推进项目"，说"已完成环评，获得开工许可证"

### E - Expert Sources (专家来源) - 强制执行
✅ 必须标注专家全名和机构：不说"专家认为"，说"摩根士丹利分析师Adam Jonas在MS-EV-2024-11报告中指出"
✅ 必须标注报告编号和发布日期
✅ 必须区分一手信息和二手引用
✅ 必须标注信息来源的权威性级别

## 信息密度要求
- 每100字必须包含至少5个具体数据点
- Shannon熵值必须达到0.8以上
- 可验证事实比例必须超过80%
- 禁止任何形式的凑字数行为

## 质量检查清单
在输出任何内容前，必须通过以下检查：
□ 是否每个段落都包含至少3个具体数据？
□ 是否所有数字都精确到个位或小数点后一位？
□ 是否所有人名都包含完整姓名和职位？
□ 是否所有时间都精确到日期？
□ 是否所有金额都包含币种和时间点？
□ 是否所有公司都包含全称和股票代码？

如果任何一项检查不通过，必须重新生成内容。
"""

    @staticmethod
    def get_platform_case_prompt(platform: Platform, research: StructuredResearch) -> str:
        """根据平台生成CASE框架特定提示词"""
        
        base_case = CASEFrameworkPrompts.get_case_enforcement_prompt()
        
        platform_specifics = {
            Platform.WECHAT: """
## 微信公众号CASE执行标准

### 字数要求：2000-3000字，信息密度必须达标

### 强制包含元素：
1. **数据图表描述**（至少5个）
   ✅ "根据中汽协数据，2024年10月新能源汽车销量95.6万辆，同比增长7.5%"
   ✅ "如下图所示，小米SU7日产量从4月的180辆提升至10月的280辆"

2. **具体公司案例**（至少3个）
   ✅ "宁德时代(300750.SZ)为小米供应磷酸铁锂电池，单车配套价格约3.2万元"
   ✅ "博世(中国)投资有限公司提供ESP系统，合同金额1.8亿元"

3. **精确数据点**（至少15个）
   ✅ 必须包含具体金额、百分比、时间、人数等

4. **专家观点引用**（至少2位）
   ✅ "国金证券分析师李海宁在2024年11月15日研报(编号:GS-AUTO-2024-115)中预测..."

### 内容结构要求：
1. 现象观察（300字，包含5个具体数据）
2. 深度分析（1200字，包含8个具体案例）  
3. 影响评估（600字，包含3个量化预测）
4. 实用建议（400字，包含具体行动步骤）
""",

            Platform.XIAOHONGSHU: """
## 小红书CASE执行标准

### 字数要求：800-1200字，必须真实体验感

### 强制包含元素：
1. **个人体验数据**（具体且可验证）
   ✅ "我实际试驾了小米SU7，0-100km/h加速实测2.78秒（官方2.78秒）"
   ✅ "充电测试：从20%到80%用时28分钟，比官方宣传的30分钟快2分钟"

2. **价格成本明细**
   ✅ "标准版售价215,900元，选装激光雷达包+5000元，总计220,900元"
   ✅ "保险费用8,640元/年，充电成本约0.8元/公里"

3. **时间记录精确**  
   ✅ "2024年11月20日下午2:30在北京亦庄交付中心提车"
   ✅ "使用3个月累计行驶4,287公里"

4. **效果量化对比**
   ✅ "相比之前开的Model 3，续航增加了87公里，充电速度提升15%"

### 语言风格：
- 姐妹感真实分享，但数据必须精确
- 每个体验必须有具体数字支撑
- 避免夸张，用事实说话
""",

            Platform.BILIBILI: """
## B站CASE执行标准  

### 视频脚本要求：8-12分钟，分章节详述

### 强制包含元素：
1. **分章节知识点**（带时间戳）
   ✅ "【02:15】产能数据分析：小米SU7目前日产280辆，月产能8,400辆"
   ✅ "【05:30】供应链解析：核心供应商包括宁德时代(电池)、博世(制动)、采埃孚(转向)"

2. **技术原理详解**
   ✅ "小米SU7采用CTC电池技术，电池包直接集成到车身结构中，刚性提升25%"
   ✅ "双电机四驱系统：前电机最大功率220kW，后电机265kW，综合功率485kW"

3. **数据可视化描述**
   ✅ "屏幕显示：2024年新能源汽车销量对比柱状图，小米SU7占比1.2%"
   ✅ "表格展示：五款竞品车型关键参数对比"

4. **深度案例分析**
   ✅ "以蔚来ET7为例，同样面临产能爬坡问题，从2022年3月的日产150辆提升至当前的580辆，用时18个月"

### 内容深度要求：
- 每个章节必须有具体数据支撑
- 技术解释必须准确专业
- 必须有行业对比和趋势分析
""",

            Platform.DOUYIN: """
## 抖音CASE执行标准

### 视频时长：30-60秒，信息密度最大化

### 强制包含元素：
1. **3秒冲击开场**
   ✅ "小米汽车日产量只有280辆！而特斯拉上海工厂日产2,000辆，差距7倍！"
   ✅ "雷军投资100亿建厂，结果产能利用率只有28%！"

2. **震撼数据对比**
   ✅ "你以为小米很强？产能数据告诉你真相：280 vs 2000，差距一目了然"
   ✅ "同样是电车，蔚来日产580辆，理想650辆，小米280辆垫底"

3. **反转认知事实**
   ✅ "小米SU7订单量27万辆，但产能缺口高达96万辆！交车要等2年！"
   ✅ "雷军说要年产30万辆，现实是年产最多10万辆，差距3倍"

4. **具体行动建议**
   ✅ "如果你订了小米SU7，建议关注这3个时间点：2024年12月产能数据、2025年3月交付计划、新工厂投产时间"

### 表达要求：
- 每句话必须有具体数字
- 对比必须震撼且准确
- 时间限制内传达最大信息量
"""
        }
        
        platform_prompt = platform_specifics.get(platform, platform_specifics[Platform.WECHAT])
        
        # 注入研究数据
        research_context = f"""
## 研究数据注入

### 核心事实数据：
{CASEFrameworkPrompts._format_research_facts(research.core_facts)}

### 关键人物信息：
{CASEFrameworkPrompts._format_key_players(research.key_players)}

### 时间线数据：
{CASEFrameworkPrompts._format_timeline(research.timeline)}

### 证据来源：
{', '.join(research.evidence_sources[:5])}

### 当前信息密度：{research.information_density:.2f}
### 置信度：{research.confidence_score:.2f}

"""
        
        return f"{base_case}\n{platform_prompt}\n{research_context}"
    
    @staticmethod  
    def _format_research_facts(facts: List[Dict[str, Any]]) -> str:
        """格式化研究事实"""
        if not facts:
            return "待补充具体事实数据"
        
        formatted = []
        for fact in facts[:5]:  # 取前5个重要事实
            money = ', '.join(fact.get('money', []))
            dates = ', '.join(fact.get('dates', []))
            people = ', '.join(fact.get('people', []))
            
            formatted.append(f"- 金额: {money}, 时间: {dates}, 人物: {people}")
        
        return '\n'.join(formatted)
    
    @staticmethod
    def _format_key_players(players: List[Dict[str, Any]]) -> str:
        """格式化关键人物"""
        if not players:
            return "待补充关键人物信息"
        
        formatted = []
        for player in players[:5]:
            name = player.get('name', '待确认')
            position = player.get('position', '待确认')  
            org = player.get('organization', '待确认')
            
            formatted.append(f"- {name} ({position}, {org})")
        
        return '\n'.join(formatted)
    
    @staticmethod
    def _format_timeline(timeline: List[Dict[str, Any]]) -> str:
        """格式化时间线"""
        if not timeline:
            return "待补充时间线数据"
        
        formatted = []
        for event in timeline[:5]:
            date = event.get('date', '待确认')
            description = event.get('event', '待补充')
            
            formatted.append(f"- {date}: {description}")
        
        return '\n'.join(formatted)

class ContentQualityEnforcer:
    """内容质量强制执行器"""
    
    def __init__(self):
        self.density_calculator = InformationDensityCalculator()
        self.min_density_score = 0.6  # 最低信息密度要求
        self.min_data_points_per_100 = 3  # 每100字最少数据点
    
    def validate_content(self, content: str, title: str) -> Dict[str, Any]:
        """验证内容质量，不达标则拒绝"""
        
        # 计算信息密度
        density_metrics = self.density_calculator.calculate_density_score(content)
        
        # 质量检查
        issues = []
        
        # 检查信息密度
        if density_metrics['total_density_score'] < self.min_density_score:
            issues.append(f"信息密度不足：{density_metrics['total_density_score']:.2f} < {self.min_density_score}")
        
        # 检查数据点密度
        if density_metrics['data_points_per_100_chars'] < self.min_data_points_per_100:
            issues.append(f"数据点密度不足：{density_metrics['data_points_per_100_chars']:.2f} < {self.min_data_points_per_100}")
        
        # 检查CASE框架合规性
        if density_metrics['case_compliance'] < 0.7:
            issues.append(f"CASE框架合规性不足：{density_metrics['case_compliance']:.2f} < 0.7")
        
        # 检查空话比例
        empty_phrases = self._detect_empty_phrases(content)
        if len(empty_phrases) > 0:
            issues.append(f"发现空话表达：{', '.join(empty_phrases[:3])}")
        
        # 检查具体数据
        specific_data_count = self._count_specific_data(content)
        if specific_data_count < 5:
            issues.append(f"具体数据不足：仅{specific_data_count}个，需要至少5个")
        
        return {
            "passed": len(issues) == 0,
            "score": density_metrics['total_density_score'],
            "grade": density_metrics['grade'],
            "issues": issues,
            "metrics": density_metrics,
            "specific_data_count": specific_data_count
        }
    
    def _detect_empty_phrases(self, content: str) -> List[str]:
        """检测空话表达"""
        empty_phrases = [
            "据了解", "有消息称", "业内人士表示", "分析认为",
            "大约", "左右", "相关", "一定程度上", "总的来说",
            "值得注意的是", "引起关注", "备受期待", "广泛讨论",
            "让我们一起", "综合来看", "从某种意义上说"
        ]
        
        found_phrases = []
        for phrase in empty_phrases:
            if phrase in content:
                found_phrases.append(phrase)
        
        return found_phrases
    
    def _count_specific_data(self, content: str) -> int:
        """统计具体数据数量"""
        import re
        
        # 具体数字+单位
        numbers = len(re.findall(r'\d+(?:\.\d+)?\s*(?:万|亿|千万|百万|%|元|美元|人|家|年|月|日|倍|次)', content))
        
        # 具体时间
        dates = len(re.findall(r'\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}', content))
        
        # 具体姓名
        names = len(re.findall(r'[A-Za-z\u4e00-\u9fa5]{2,4}(?:先生|女士|教授|博士|总裁|董事长|CEO)', content))
        
        # 具体公司
        companies = len(re.findall(r'[A-Za-z\u4e00-\u9fa5]{2,10}(?:公司|集团|科技|有限公司|股份|Corp|Inc|Ltd)', content))
        
        return numbers + dates + names + companies

def get_enhanced_content_generation_prompt(platform: Platform, research: StructuredResearch) -> str:
    """获取增强版内容生成提示词"""
    
    case_prompt = CASEFrameworkPrompts.get_platform_case_prompt(platform, research)
    
    quality_enforcement = """
## 最终质量要求

生成的内容必须通过以下严格检查：

1. **信息密度检查**
   - Shannon熵 ≥ 0.8
   - 每100字包含 ≥ 5个具体数据点
   - CASE框架合规性 ≥ 70%

2. **事实准确性检查**  
   - 所有数字必须可验证
   - 所有人名必须准确完整
   - 所有时间必须精确到日
   - 所有来源必须可追溯

3. **内容价值检查**
   - 提供独特洞察或信息
   - 回答用户核心关切
   - 具有可操作的建议
   - 避免重复已知信息

如果内容不满足以上任何一项要求，将被系统拒绝并要求重新生成。

现在，基于提供的深度研究数据，生成符合所有要求的高质量内容。
"""
    
    return f"{case_prompt}\n{quality_enforcement}"

# 使用示例
def example_enhanced_prompt_usage():
    """增强提示词使用示例"""
    
    # 模拟研究数据
    mock_research = StructuredResearch(
        core_facts=[
            {
                "type": "financial_data",
                "money": ["158.6亿元"],
                "dates": ["2024年11月28日"],
                "people": ["雷军", "王翔"],
                "source": "official_report"
            }
        ],
        key_players=[
            {
                "name": "雷军",
                "position": "董事长兼CEO", 
                "organization": "小米集团",
                "role_in_event": "决策者"
            }
        ],
        timeline=[
            {
                "date": "2024年3月28日",
                "event": "小米SU7正式发布",
                "impact": "订单量突破5万辆"
            }
        ],
        hidden_details=[],
        evidence_sources=["小米集团2024年Q3财报", "中汽协月度数据"],
        confidence_score=0.85,
        information_density=0.76
    )
    
    # 生成微信公众号提示词
    wechat_prompt = get_enhanced_content_generation_prompt(Platform.WECHAT, mock_research)
    
    print("📝 增强版微信公众号提示词已生成")
    print(f"提示词长度: {len(wechat_prompt)} 字符")
    
    # 质量验证
    enforcer = ContentQualityEnforcer()
    sample_content = "小米SU7在2024年11月28日的产能数据显示，日产量仅280辆，相比特斯拉上海工厂的2000辆日产能差距巨大。"
    
    validation = enforcer.validate_content(sample_content, "小米SU7产能分析")
    print(f"\n📊 内容质量检查: {'通过' if validation['passed'] else '不通过'}")
    print(f"质量评分: {validation['score']:.2f}")
    print(f"质量等级: {validation['grade']}")

if __name__ == "__main__":
    example_enhanced_prompt_usage()
