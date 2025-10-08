// 火灾应急救援知识图谱示例数据
// 创建材质节点
CREATE (m1:Material {name: "木材", category: "可燃材料"})
CREATE (m2:Material {name: "塑料", category: "可燃材料"})
CREATE (m3:Material {name: "金属", category: "不可燃材料"})
CREATE (m4:Material {name: "纸张", category: "可燃材料"})
CREATE (m5:Material {name: "布料", category: "可燃材料"})
CREATE (m6:Material {name: "汽油", category: "易燃液体"})
CREATE (m7:Material {name: "天然气", category: "易燃气体"})

// 创建材质属性
CREATE (p1:Property {key: "燃点", value: "300°C"})
CREATE (p2:Property {key: "燃点", value: "400°C"})
CREATE (p3:Property {key: "燃点", value: "不燃"})
CREATE (p4:Property {key: "燃点", value: "233°C"})
CREATE (p5:Property {key: "燃点", value: "250°C"})
CREATE (p6:Property {key: "燃点", value: "-43°C"})
CREATE (p7:Property {key: "燃点", value: "537°C"})

// 创建危险特性
CREATE (h1:Hazard {description: "燃烧时产生大量烟雾"})
CREATE (h2:Hazard {description: "燃烧时产生有毒气体"})
CREATE (h3:Hazard {description: "高温下可能爆炸"})
CREATE (h4:Hazard {description: "燃烧速度快"})
CREATE (h5:Hazard {description: "燃烧时产生明火"})

// 创建安全措施
CREATE (s1:SafetyMeasure {description: "使用水灭火"})
CREATE (s2:SafetyMeasure {description: "使用泡沫灭火器"})
CREATE (s3:SafetyMeasure {description: "使用干粉灭火器"})
CREATE (s4:SafetyMeasure {description: "使用二氧化碳灭火器"})
CREATE (s5:SafetyMeasure {description: "切断气源"})

// 创建环境节点
CREATE (e1:Environment {location: "住宅", type: "室内"})
CREATE (e2:Environment {location: "工厂", type: "工业"})
CREATE (e3:Environment {location: "森林", type: "户外"})
CREATE (e4:Environment {location: "车库", type: "半封闭"})
CREATE (e5:Environment {location: "厨房", type: "室内"})

// 创建环境条件
CREATE (c1:Condition {key: "温度", value: "常温"})
CREATE (c2:Condition {key: "湿度", value: "干燥"})
CREATE (c3:Condition {key: "通风", value: "良好"})
CREATE (c4:Condition {key: "温度", value: "高温"})
CREATE (c5:Condition {key: "湿度", value: "潮湿"})

// 创建风险因素
CREATE (r1:Risk {description: "火势蔓延快"})
CREATE (r2:Risk {description: "烟雾浓度高"})
CREATE (r3:Risk {description: "有毒气体"})
CREATE (r4:Risk {description: "爆炸危险"})
CREATE (r5:Risk {description: "结构坍塌"})

// 创建建议措施
CREATE (rec1:Recommendation {description: "立即疏散人员"})
CREATE (rec2:Recommendation {description: "关闭电源"})
CREATE (rec3:Recommendation {description: "关闭气源"})
CREATE (rec4:Recommendation {description: "使用适当灭火器"})
CREATE (rec5:Recommendation {description: "保持安全距离"})

// 创建救援程序
CREATE (proc1:Procedure {
    id: "PROC001",
    title: "木材火灾救援程序",
    description: "处理木材火灾的标准救援程序",
    priority: 1
})
CREATE (proc2:Procedure {
    id: "PROC002", 
    title: "液体燃料火灾救援程序",
    description: "处理液体燃料火灾的救援程序",
    priority: 2
})
CREATE (proc3:Procedure {
    id: "PROC003",
    title: "气体火灾救援程序", 
    description: "处理气体火灾的救援程序",
    priority: 3
})

// 创建步骤
CREATE (step1:Step {description: "评估火势大小和蔓延情况"})
CREATE (step2:Step {description: "确定安全撤离路线"})
CREATE (step3:Step {description: "选择合适的灭火器材"})
CREATE (step4:Step {description: "从安全距离开始灭火"})
CREATE (step5:Step {description: "监控火势变化"})
CREATE (step6:Step {description: "确保火势完全扑灭"})

// 创建安全注意事项
CREATE (sn1:SafetyNote {description: "注意烟雾中毒"})
CREATE (sn2:SafetyNote {description: "防止复燃"})
CREATE (sn3:SafetyNote {description: "避免用水扑灭油火"})
CREATE (sn4:SafetyNote {description: "保持通风"})
CREATE (sn5:SafetyNote {description: "穿戴防护装备"})

// 建立材质-属性关系
CREATE (m1)-[:HAS_PROPERTY]->(p1)
CREATE (m2)-[:HAS_PROPERTY]->(p2)
CREATE (m3)-[:HAS_PROPERTY]->(p3)
CREATE (m4)-[:HAS_PROPERTY]->(p4)
CREATE (m5)-[:HAS_PROPERTY]->(p5)
CREATE (m6)-[:HAS_PROPERTY]->(p6)
CREATE (m7)-[:HAS_PROPERTY]->(p7)

// 建立材质-危险特性关系
CREATE (m1)-[:HAS_HAZARD]->(h1)
CREATE (m1)-[:HAS_HAZARD]->(h4)
CREATE (m2)-[:HAS_HAZARD]->(h2)
CREATE (m2)-[:HAS_HAZARD]->(h4)
CREATE (m4)-[:HAS_HAZARD]->(h1)
CREATE (m4)-[:HAS_HAZARD]->(h4)
CREATE (m5)-[:HAS_HAZARD]->(h1)
CREATE (m5)-[:HAS_HAZARD]->(h4)
CREATE (m6)-[:HAS_HAZARD]->(h3)
CREATE (m6)-[:HAS_HAZARD]->(h4)
CREATE (m6)-[:HAS_HAZARD]->(h5)
CREATE (m7)-[:HAS_HAZARD]->(h3)
CREATE (m7)-[:HAS_HAZARD]->(h5)

// 建立材质-安全措施关系
CREATE (m1)-[:HAS_SAFETY_MEASURE]->(s1)
CREATE (m1)-[:HAS_SAFETY_MEASURE]->(s2)
CREATE (m2)-[:HAS_SAFETY_MEASURE]->(s3)
CREATE (m2)-[:HAS_SAFETY_MEASURE]->(s4)
CREATE (m4)-[:HAS_SAFETY_MEASURE]->(s1)
CREATE (m4)-[:HAS_SAFETY_MEASURE]->(s2)
CREATE (m5)-[:HAS_SAFETY_MEASURE]->(s1)
CREATE (m5)-[:HAS_SAFETY_MEASURE]->(s2)
CREATE (m6)-[:HAS_SAFETY_MEASURE]->(s3)
CREATE (m6)-[:HAS_SAFETY_MEASURE]->(s4)
CREATE (m7)-[:HAS_SAFETY_MEASURE]->(s5)
CREATE (m7)-[:HAS_SAFETY_MEASURE]->(s4)

// 建立环境-条件关系
CREATE (e1)-[:HAS_CONDITION]->(c1)
CREATE (e1)-[:HAS_CONDITION]->(c3)
CREATE (e2)-[:HAS_CONDITION]->(c4)
CREATE (e2)-[:HAS_CONDITION]->(c2)
CREATE (e3)-[:HAS_CONDITION]->(c1)
CREATE (e3)-[:HAS_CONDITION]->(c5)
CREATE (e4)-[:HAS_CONDITION]->(c1)
CREATE (e5)-[:HAS_CONDITION]->(c1)
CREATE (e5)-[:HAS_CONDITION]->(c3)

// 建立环境-风险关系
CREATE (e1)-[:HAS_RISK]->(r1)
CREATE (e1)-[:HAS_RISK]->(r2)
CREATE (e2)-[:HAS_RISK]->(r1)
CREATE (e2)-[:HAS_RISK]->(r3)
CREATE (e2)-[:HAS_RISK]->(r4)
CREATE (e3)-[:HAS_RISK]->(r1)
CREATE (e3)-[:HAS_RISK]->(r5)
CREATE (e4)-[:HAS_RISK]->(r4)
CREATE (e5)-[:HAS_RISK]->(r1)

// 建立环境-建议关系
CREATE (e1)-[:HAS_RECOMMENDATION]->(rec1)
CREATE (e1)-[:HAS_RECOMMENDATION]->(rec2)
CREATE (e2)-[:HAS_RECOMMENDATION]->(rec1)
CREATE (e2)-[:HAS_RECOMMENDATION]->(rec3)
CREATE (e2)-[:HAS_RECOMMENDATION]->(rec4)
CREATE (e3)-[:HAS_RECOMMENDATION]->(rec1)
CREATE (e3)-[:HAS_RECOMMENDATION]->(rec5)
CREATE (e4)-[:HAS_RECOMMENDATION]->(rec3)
CREATE (e4)-[:HAS_RECOMMENDATION]->(rec4)
CREATE (e5)-[:HAS_RECOMMENDATION]->(rec2)
CREATE (e5)-[:HAS_RECOMMENDATION]->(rec3)

// 建立程序-步骤关系
CREATE (proc1)-[:HAS_STEP]->(step1)
CREATE (proc1)-[:HAS_STEP]->(step2)
CREATE (proc1)-[:HAS_STEP]->(step3)
CREATE (proc1)-[:HAS_STEP]->(step4)
CREATE (proc1)-[:HAS_STEP]->(step5)
CREATE (proc1)-[:HAS_STEP]->(step6)

CREATE (proc2)-[:HAS_STEP]->(step1)
CREATE (proc2)-[:HAS_STEP]->(step2)
CREATE (proc2)-[:HAS_STEP]->(step3)
CREATE (proc2)-[:HAS_STEP]->(step4)
CREATE (proc2)-[:HAS_STEP]->(step5)
CREATE (proc2)-[:HAS_STEP]->(step6)

CREATE (proc3)-[:HAS_STEP]->(step1)
CREATE (proc3)-[:HAS_STEP]->(step2)
CREATE (proc3)-[:HAS_STEP]->(step3)
CREATE (proc3)-[:HAS_STEP]->(step4)
CREATE (proc3)-[:HAS_STEP]->(step5)
CREATE (proc3)-[:HAS_STEP]->(step6)

// 建立程序-材料关系
CREATE (proc1)-[:REQUIRES_MATERIAL]->(m1)
CREATE (proc1)-[:REQUIRES_MATERIAL]->(m4)
CREATE (proc1)-[:REQUIRES_MATERIAL]->(m5)
CREATE (proc2)-[:REQUIRES_MATERIAL]->(m6)
CREATE (proc3)-[:REQUIRES_MATERIAL]->(m7)

// 建立程序-安全注意事项关系
CREATE (proc1)-[:HAS_SAFETY_NOTE]->(sn1)
CREATE (proc1)-[:HAS_SAFETY_NOTE]->(sn2)
CREATE (proc2)-[:HAS_SAFETY_NOTE]->(sn3)
CREATE (proc2)-[:HAS_SAFETY_NOTE]->(sn4)
CREATE (proc3)-[:HAS_SAFETY_NOTE]->(sn5)
CREATE (proc3)-[:HAS_SAFETY_NOTE]->(sn2)

// 建立程序-适用材质关系
CREATE (proc1)-[:APPLIES_TO]->(m1)
CREATE (proc1)-[:APPLIES_TO]->(m4)
CREATE (proc1)-[:APPLIES_TO]->(m5)
CREATE (proc2)-[:APPLIES_TO]->(m6)
CREATE (proc3)-[:APPLIES_TO]->(m7)

// 建立程序-适用环境关系
CREATE (proc1)-[:APPLIES_TO]->(e1)
CREATE (proc1)-[:APPLIES_TO]->(e3)
CREATE (proc2)-[:APPLIES_TO]->(e2)
CREATE (proc2)-[:APPLIES_TO]->(e4)
CREATE (proc3)-[:APPLIES_TO]->(e2)
CREATE (proc3)-[:APPLIES_TO]->(e5)

// 建立材质-相关材质关系
CREATE (m1)-[:RELATED_TO]->(m4)
CREATE (m1)-[:RELATED_TO]->(m5)
CREATE (m2)-[:RELATED_TO]->(m6)
CREATE (m4)-[:RELATED_TO]->(m1)
CREATE (m4)-[:RELATED_TO]->(m5)
CREATE (m5)-[:RELATED_TO]->(m1)
CREATE (m5)-[:RELATED_TO]->(m4)
CREATE (m6)-[:RELATED_TO]->(m2)
CREATE (m6)-[:RELATED_TO]->(m7)
CREATE (m7)-[:RELATED_TO]->(m6)
