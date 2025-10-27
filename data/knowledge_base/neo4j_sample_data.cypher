// 火灾应急救援RAG系统 - Neo4j示例数据
// 创建物品节点
CREATE (item1:Item {
    id: 'item_001',
    name: '椅子',
    material: '木质',
    flammability: '易燃',
    toxicity: '低',
    category: '家具',
    weight: '5kg',
    size: '50x50x80cm'
})

CREATE (item2:Item {
    id: 'item_002',
    name: '桌子',
    material: '木质',
    flammability: '易燃',
    toxicity: '低',
    category: '家具',
    weight: '20kg',
    size: '120x60x75cm'
})

CREATE (item3:Item {
    id: 'item_003',
    name: '冰箱',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '电器',
    weight: '60kg',
    size: '60x60x180cm'
})

CREATE (item4:Item {
    id: 'item_004',
    name: '沙发',
    material: '布料',
    flammability: '易燃',
    toxicity: '中',
    category: '家具',
    weight: '40kg',
    size: '200x80x80cm'
})

CREATE (item5:Item {
    id: 'item_005',
    name: '电视机',
    material: '塑料',
    flammability: '易燃',
    toxicity: '高',
    category: '电器',
    weight: '15kg',
    size: '100x60x10cm'
})

CREATE (item6:Item {
    id: 'item_006',
    name: '床垫',
    material: '泡沫',
    flammability: '极易燃',
    toxicity: '高',
    category: '家具',
    weight: '25kg',
    size: '200x150x20cm'
})

CREATE (item7:Item {
    id: 'item_007',
    name: '窗帘',
    material: '布料',
    flammability: '易燃',
    toxicity: '中',
    category: '装饰',
    weight: '2kg',
    size: '300x200x1cm'
})

CREATE (item8:Item {
    id: 'item_008',
    name: '燃气灶',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '厨房',
    weight: '30kg',
    size: '60x40x15cm'
})

// 创建材质节点
CREATE (material1:Material {
    id: 'material_001',
    name: '木质',
    flammability_level: '高',
    toxicity_level: '低',
    ignition_point: 300,
    melting_point: null,
    density: '0.6g/cm³',
    description: '天然木材，易燃但毒性较低'
})

CREATE (material2:Material {
    id: 'material_002',
    name: '金属',
    flammability_level: '低',
    toxicity_level: '低',
    ignition_point: null,
    melting_point: 1500,
    density: '7.8g/cm³',
    description: '金属材料，不燃但高温下可能变形'
})

CREATE (material3:Material {
    id: 'material_003',
    name: '布料',
    flammability_level: '高',
    toxicity_level: '中',
    ignition_point: 250,
    melting_point: null,
    density: '0.3g/cm³',
    description: '纺织材料，易燃且燃烧时产生有毒气体'
})

CREATE (material4:Material {
    id: 'material_004',
    name: '塑料',
    flammability_level: '高',
    toxicity_level: '高',
    ignition_point: 200,
    melting_point: 120,
    density: '1.2g/cm³',
    description: '合成材料，易燃且燃烧时产生大量有毒气体'
})

CREATE (material5:Material {
    id: 'material_005',
    name: '泡沫',
    flammability_level: '极高',
    toxicity_level: '高',
    ignition_point: 150,
    melting_point: 80,
    density: '0.1g/cm³',
    description: '聚氨酯泡沫，极易燃且燃烧迅速'
})

// 创建环境节点
CREATE (env1:Environment {
    id: 'env_001',
    name: '室内住宅',
    type: '室内',
    area: '住宅',
    fire_characteristics: '烟雾扩散快，温度上升迅速',
    ventilation_level: '一般',
    evacuation_difficulty: '中等',
    floor_range: '1-6层',
    occupancy_density: '低'
})

CREATE (env2:Environment {
    id: 'env_002',
    name: '高层住宅',
    type: '室内',
    area: '住宅',
    fire_characteristics: '烟囱效应明显，疏散困难',
    ventilation_level: '差',
    evacuation_difficulty: '高',
    floor_range: '7层以上',
    occupancy_density: '高'
})

CREATE (env3:Environment {
    id: 'env_003',
    name: '商业建筑',
    type: '室内',
    area: '商业',
    fire_characteristics: '人员密集，疏散复杂',
    ventilation_level: '良好',
    evacuation_difficulty: '高',
    floor_range: '多层',
    occupancy_density: '极高'
})

CREATE (env4:Environment {
    id: 'env_004',
    name: '工业厂房',
    type: '室内',
    area: '工业',
    fire_characteristics: '可燃物多，火势蔓延快',
    ventilation_level: '一般',
    evacuation_difficulty: '中等',
    floor_range: '单层',
    occupancy_density: '中等'
})

CREATE (env5:Environment {
    id: 'env_005',
    name: '室外广场',
    type: '室外',
    area: '公共',
    fire_characteristics: '通风良好，火势相对可控',
    ventilation_level: '极好',
    evacuation_difficulty: '低',
    floor_range: '地面',
    occupancy_density: '变化'
})

// 创建救援方案节点
CREATE (plan1:RescuePlan {
    id: 'plan_001',
    name: '木质家具火灾救援',
    priority: '高',
    steps: [
        '立即疏散所有人员',
        '关闭电源和燃气',
        '使用干粉灭火器扑救',
        '如无法控制，立即撤离并报警',
        '确保安全距离至少10米'
    ],
    equipment: ['干粉灭火器', '湿毛巾', '安全绳', '手电筒'],
    warnings: [
        '木质家具燃烧迅速，注意火势蔓延',
        '避免使用水扑救电器火灾',
        '确保自身安全，不要冒险'
    ],
    estimated_duration: 15,
    success_rate: 0.85
})

CREATE (plan2:RescuePlan {
    id: 'plan_002',
    name: '电器火灾救援',
    priority: '紧急',
    steps: [
        '立即切断电源',
        '疏散所有人员',
        '使用二氧化碳灭火器',
        '严禁使用水或泡沫灭火器',
        '如无法控制，立即撤离'
    ],
    equipment: ['二氧化碳灭火器', '绝缘手套', '安全绳', '手电筒'],
    warnings: [
        '电器火灾有触电危险',
        '必须切断电源才能扑救',
        '使用错误的灭火剂可能造成爆炸'
    ],
    estimated_duration: 10,
    success_rate: 0.90
})

CREATE (plan3:RescuePlan {
    id: 'plan_003',
    name: '布料火灾救援',
    priority: '高',
    steps: [
        '立即疏散人员',
        '使用湿毛巾覆盖火源',
        '使用干粉或泡沫灭火器',
        '注意防止复燃',
        '确保通风良好'
    ],
    equipment: ['湿毛巾', '干粉灭火器', '泡沫灭火器', '水桶'],
    warnings: [
        '布料燃烧产生有毒气体',
        '注意防止烟雾中毒',
        '确保通风，避免窒息'
    ],
    estimated_duration: 12,
    success_rate: 0.80
})

CREATE (plan4:RescuePlan {
    id: 'plan_004',
    name: '塑料火灾救援',
    priority: '紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有门窗',
        '使用干粉灭火器',
        '严禁使用水扑救',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '安全绳', '手电筒'],
    warnings: [
        '塑料燃烧产生剧毒气体',
        '必须佩戴防毒面具',
        '塑料熔化后可能造成严重烧伤'
    ],
    estimated_duration: 8,
    success_rate: 0.75
})

CREATE (plan5:RescuePlan {
    id: 'plan_005',
    name: '泡沫材料火灾救援',
    priority: '极紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有通风口',
        '使用干粉灭火器',
        '严禁使用水或泡沫',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '安全绳', '手电筒'],
    warnings: [
        '泡沫材料燃烧极快',
        '产生大量有毒气体',
        '火势蔓延极快，难以控制'
    ],
    estimated_duration: 5,
    success_rate: 0.60
})

// 创建关系
// 物品-材质关系
MATCH (item1:Item {id: 'item_001'}), (material1:Material {id: 'material_001'})
CREATE (item1)-[:HAS_MATERIAL {strength: 'strong'}]->(material1)

MATCH (item2:Item {id: 'item_002'}), (material1:Material {id: 'material_001'})
CREATE (item2)-[:HAS_MATERIAL {strength: 'strong'}]->(material1)

MATCH (item3:Item {id: 'item_003'}), (material2:Material {id: 'material_002'})
CREATE (item3)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

MATCH (item4:Item {id: 'item_004'}), (material3:Material {id: 'material_003'})
CREATE (item4)-[:HAS_MATERIAL {strength: 'strong'}]->(material3)

MATCH (item5:Item {id: 'item_005'}), (material4:Material {id: 'material_004'})
CREATE (item5)-[:HAS_MATERIAL {strength: 'strong'}]->(material4)

MATCH (item6:Item {id: 'item_006'}), (material5:Material {id: 'material_005'})
CREATE (item6)-[:HAS_MATERIAL {strength: 'strong'}]->(material5)

MATCH (item7:Item {id: 'item_007'}), (material3:Material {id: 'material_003'})
CREATE (item7)-[:HAS_MATERIAL {strength: 'strong'}]->(material3)

MATCH (item8:Item {id: 'item_008'}), (material2:Material {id: 'material_002'})
CREATE (item8)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

// 材质-救援方案关系
MATCH (material1:Material {id: 'material_001'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (material1)-[:REQUIRES_RESCUE_PLAN {applicability: 0.9}]->(plan1)

MATCH (material2:Material {id: 'material_002'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (material2)-[:REQUIRES_RESCUE_PLAN {applicability: 0.95}]->(plan2)

MATCH (material3:Material {id: 'material_003'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (material3)-[:REQUIRES_RESCUE_PLAN {applicability: 0.85}]->(plan3)

MATCH (material4:Material {id: 'material_004'}), (plan4:RescuePlan {id: 'plan_004'})
CREATE (material4)-[:REQUIRES_RESCUE_PLAN {applicability: 0.9}]->(plan4)

MATCH (material5:Material {id: 'material_005'}), (plan5:RescuePlan {id: 'plan_005'})
CREATE (material5)-[:REQUIRES_RESCUE_PLAN {applicability: 0.95}]->(plan5)

// 环境-救援方案关系
MATCH (env1:Environment {id: 'env_001'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (env1)-[:SUITABLE_FOR {effectiveness: 0.8}]->(plan1)

MATCH (env1:Environment {id: 'env_001'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (env1)-[:SUITABLE_FOR {effectiveness: 0.9}]->(plan2)

MATCH (env2:Environment {id: 'env_002'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (env2)-[:SUITABLE_FOR {effectiveness: 0.7}]->(plan1)

MATCH (env3:Environment {id: 'env_003'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (env3)-[:SUITABLE_FOR {effectiveness: 0.85}]->(plan2)

MATCH (env4:Environment {id: 'env_004'}), (plan4:RescuePlan {id: 'plan_004'})
CREATE (env4)-[:SUITABLE_FOR {effectiveness: 0.9}]->(plan4)

// 物品-救援方案关系
MATCH (item1:Item {id: 'item_001'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (item1)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan1)

MATCH (item2:Item {id: 'item_002'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (item2)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan1)

MATCH (item3:Item {id: 'item_003'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item3)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item4:Item {id: 'item_004'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (item4)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan3)

MATCH (item5:Item {id: 'item_005'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item5)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item6:Item {id: 'item_006'}), (plan5:RescuePlan {id: 'plan_005'})
CREATE (item6)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan5)

MATCH (item7:Item {id: 'item_007'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (item7)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan3)

MATCH (item8:Item {id: 'item_008'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item8)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

// 扩展物品节点
CREATE (item9:Item {
    id: 'item_009',
    name: '床',
    material: '木质',
    flammability: '易燃',
    toxicity: '低',
    category: '家具',
    weight: '80kg',
    size: '200x150x30cm'
})

CREATE (item10:Item {
    id: 'item_010',
    name: '衣柜',
    material: '木质',
    flammability: '易燃',
    toxicity: '低',
    category: '家具',
    weight: '120kg',
    size: '200x60x200cm'
})

CREATE (item11:Item {
    id: 'item_011',
    name: '空调',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '电器',
    weight: '35kg',
    size: '80x30x20cm'
})

CREATE (item12:Item {
    id: 'item_012',
    name: '洗衣机',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '电器',
    weight: '50kg',
    size: '60x60x85cm'
})

CREATE (item13:Item {
    id: 'item_013',
    name: '地毯',
    material: '布料',
    flammability: '易燃',
    toxicity: '中',
    category: '装饰',
    weight: '15kg',
    size: '300x200x2cm'
})

CREATE (item14:Item {
    id: 'item_014',
    name: '书桌',
    material: '木质',
    flammability: '易燃',
    toxicity: '低',
    category: '家具',
    weight: '25kg',
    size: '120x60x75cm'
})

CREATE (item15:Item {
    id: 'item_015',
    name: '电脑',
    material: '塑料',
    flammability: '易燃',
    toxicity: '高',
    category: '电器',
    weight: '5kg',
    size: '40x30x10cm'
})

CREATE (item16:Item {
    id: 'item_016',
    name: '微波炉',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '电器',
    weight: '20kg',
    size: '50x40x30cm'
})

CREATE (item17:Item {
    id: 'item_017',
    name: '轮胎',
    material: '橡胶',
    flammability: '易燃',
    toxicity: '中',
    category: '汽车配件',
    weight: '12kg',
    size: '直径60cm'
})

CREATE (item18:Item {
    id: 'item_018',
    name: '玻璃窗',
    material: '玻璃',
    flammability: '不燃',
    toxicity: '低',
    category: '建筑',
    weight: '20kg',
    size: '120x80x1cm'
})

CREATE (item19:Item {
    id: 'item_019',
    name: '陶瓷花瓶',
    material: '陶瓷',
    flammability: '不燃',
    toxicity: '低',
    category: '装饰',
    weight: '3kg',
    size: '30x30x50cm'
})

CREATE (item20:Item {
    id: 'item_020',
    name: '工具箱',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '工具',
    weight: '8kg',
    size: '40x25x15cm'
})

// 扩展材质节点
CREATE (material6:Material {
    id: 'material_006',
    name: '橡胶',
    flammability_level: '中',
    toxicity_level: '中',
    ignition_point: 400,
    melting_point: 120,
    density: '1.2g/cm³',
    description: '橡胶材料，中等易燃性，燃烧时产生有毒气体'
})

CREATE (material7:Material {
    id: 'material_007',
    name: '玻璃',
    flammability_level: '不燃',
    toxicity_level: '低',
    ignition_point: null,
    melting_point: 1500,
    density: '2.5g/cm³',
    description: '玻璃材料，不燃但高温下可能破裂'
})

CREATE (material8:Material {
    id: 'material_008',
    name: '陶瓷',
    flammability_level: '不燃',
    toxicity_level: '低',
    ignition_point: null,
    melting_point: 1800,
    density: '2.3g/cm³',
    description: '陶瓷材料，不燃且耐高温'
})

CREATE (material9:Material {
    id: 'material_009',
    name: '复合材料',
    flammability_level: '高',
    toxicity_level: '高',
    ignition_point: 250,
    melting_point: 100,
    density: '1.5g/cm³',
    description: '复合材料，易燃且燃烧时产生大量有毒气体'
})

CREATE (material10:Material {
    id: 'material_010',
    name: '皮革',
    flammability_level: '中',
    toxicity_level: '中',
    ignition_point: 350,
    melting_point: null,
    density: '0.9g/cm³',
    description: '皮革材料，中等易燃性，燃烧时产生刺激性气体'
})

// 扩展环境节点
CREATE (env6:Environment {
    id: 'env_006',
    name: '学校教室',
    type: '室内',
    area: '教育',
    fire_characteristics: '人员密集，疏散复杂',
    ventilation_level: '一般',
    evacuation_difficulty: '高',
    floor_range: '1-6层',
    occupancy_density: '极高'
})

CREATE (env7:Environment {
    id: 'env_007',
    name: '医院病房',
    type: '室内',
    area: '医疗',
    fire_characteristics: '患者行动不便，疏散困难',
    ventilation_level: '良好',
    evacuation_difficulty: '极高',
    floor_range: '多层',
    occupancy_density: '高'
})

CREATE (env8:Environment {
    id: 'env_008',
    name: '地下车库',
    type: '室内',
    area: '住宅',
    fire_characteristics: '通风差，烟雾积聚',
    ventilation_level: '很差',
    evacuation_difficulty: '高',
    floor_range: '地下',
    occupancy_density: '低'
})

CREATE (env9:Environment {
    id: 'env_009',
    name: '厨房',
    type: '室内',
    area: '住宅',
    fire_characteristics: '可燃物多，火势蔓延快',
    ventilation_level: '一般',
    evacuation_difficulty: '中等',
    floor_range: '任意',
    occupancy_density: '低'
})

CREATE (env10:Environment {
    id: 'env_010',
    name: '图书馆',
    type: '室内',
    area: '教育',
    fire_characteristics: '纸质材料多，火势蔓延极快',
    ventilation_level: '一般',
    evacuation_difficulty: '高',
    floor_range: '多层',
    occupancy_density: '中等'
})

// 扩展救援方案节点
CREATE (plan6:RescuePlan {
    id: 'plan_006',
    name: '橡胶制品火灾救援',
    priority: '中',
    steps: [
        '立即疏散所有人员',
        '使用干粉灭火器扑救',
        '注意防止复燃',
        '确保通风良好',
        '如无法控制，立即撤离'
    ],
    equipment: ['干粉灭火器', '湿毛巾', '安全绳', '手电筒'],
    warnings: [
        '橡胶燃烧产生有毒气体',
        '注意防止烟雾中毒',
        '确保通风，避免窒息'
    ],
    estimated_duration: 12,
    success_rate: 0.80
})

CREATE (plan7:RescuePlan {
    id: 'plan_007',
    name: '玻璃制品火灾救援',
    priority: '低',
    steps: [
        '立即疏散人员',
        '使用干粉灭火器',
        '注意玻璃碎片',
        '确保安全距离',
        '清理现场'
    ],
    equipment: ['干粉灭火器', '防护手套', '安全绳', '手电筒'],
    warnings: [
        '玻璃高温下可能破裂',
        '注意玻璃碎片伤人',
        '确保安全距离'
    ],
    estimated_duration: 8,
    success_rate: 0.90
})

CREATE (plan8:RescuePlan {
    id: 'plan_008',
    name: '陶瓷制品火灾救援',
    priority: '低',
    steps: [
        '立即疏散人员',
        '使用干粉灭火器',
        '注意高温烫伤',
        '确保安全距离',
        '清理现场'
    ],
    equipment: ['干粉灭火器', '防护手套', '安全绳', '手电筒'],
    warnings: [
        '陶瓷高温下可能破裂',
        '注意高温烫伤',
        '确保安全距离'
    ],
    estimated_duration: 6,
    success_rate: 0.95
})

CREATE (plan9:RescuePlan {
    id: 'plan_009',
    name: '复合材料火灾救援',
    priority: '紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有门窗',
        '使用干粉灭火器',
        '严禁使用水扑救',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '安全绳', '手电筒'],
    warnings: [
        '复合材料燃烧产生剧毒气体',
        '必须佩戴防毒面具',
        '复合材料熔化后可能造成严重烧伤'
    ],
    estimated_duration: 10,
    success_rate: 0.70
})

CREATE (plan10:RescuePlan {
    id: 'plan_010',
    name: '皮革制品火灾救援',
    priority: '中',
    steps: [
        '立即疏散人员',
        '使用干粉灭火器扑救',
        '注意防止复燃',
        '确保通风良好',
        '如无法控制，立即撤离'
    ],
    equipment: ['干粉灭火器', '湿毛巾', '安全绳', '手电筒'],
    warnings: [
        '皮革燃烧产生刺激性气体',
        '注意防止烟雾中毒',
        '确保通风，避免窒息'
    ],
    estimated_duration: 10,
    success_rate: 0.85
})

// 扩展关系
// 新物品-材质关系
MATCH (item9:Item {id: 'item_009'}), (material1:Material {id: 'material_001'})
CREATE (item9)-[:HAS_MATERIAL {strength: 'strong'}]->(material1)

MATCH (item10:Item {id: 'item_010'}), (material1:Material {id: 'material_001'})
CREATE (item10)-[:HAS_MATERIAL {strength: 'strong'}]->(material1)

MATCH (item11:Item {id: 'item_011'}), (material2:Material {id: 'material_002'})
CREATE (item11)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

MATCH (item12:Item {id: 'item_012'}), (material2:Material {id: 'material_002'})
CREATE (item12)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

MATCH (item13:Item {id: 'item_013'}), (material3:Material {id: 'material_003'})
CREATE (item13)-[:HAS_MATERIAL {strength: 'strong'}]->(material3)

MATCH (item14:Item {id: 'item_014'}), (material1:Material {id: 'material_001'})
CREATE (item14)-[:HAS_MATERIAL {strength: 'strong'}]->(material1)

MATCH (item15:Item {id: 'item_015'}), (material4:Material {id: 'material_004'})
CREATE (item15)-[:HAS_MATERIAL {strength: 'strong'}]->(material4)

MATCH (item16:Item {id: 'item_016'}), (material2:Material {id: 'material_002'})
CREATE (item16)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

MATCH (item17:Item {id: 'item_017'}), (material6:Material {id: 'material_006'})
CREATE (item17)-[:HAS_MATERIAL {strength: 'strong'}]->(material6)

MATCH (item18:Item {id: 'item_018'}), (material7:Material {id: 'material_007'})
CREATE (item18)-[:HAS_MATERIAL {strength: 'strong'}]->(material7)

MATCH (item19:Item {id: 'item_019'}), (material8:Material {id: 'material_008'})
CREATE (item19)-[:HAS_MATERIAL {strength: 'strong'}]->(material8)

MATCH (item20:Item {id: 'item_020'}), (material2:Material {id: 'material_002'})
CREATE (item20)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

// 新材质-救援方案关系
MATCH (material6:Material {id: 'material_006'}), (plan6:RescuePlan {id: 'plan_006'})
CREATE (material6)-[:REQUIRES_RESCUE_PLAN {applicability: 0.85}]->(plan6)

MATCH (material7:Material {id: 'material_007'}), (plan7:RescuePlan {id: 'plan_007'})
CREATE (material7)-[:REQUIRES_RESCUE_PLAN {applicability: 0.90}]->(plan7)

MATCH (material8:Material {id: 'material_008'}), (plan8:RescuePlan {id: 'plan_008'})
CREATE (material8)-[:REQUIRES_RESCUE_PLAN {applicability: 0.95}]->(plan8)

MATCH (material9:Material {id: 'material_009'}), (plan9:RescuePlan {id: 'plan_009'})
CREATE (material9)-[:REQUIRES_RESCUE_PLAN {applicability: 0.90}]->(plan9)

MATCH (material10:Material {id: 'material_010'}), (plan10:RescuePlan {id: 'plan_010'})
CREATE (material10)-[:REQUIRES_RESCUE_PLAN {applicability: 0.85}]->(plan10)

// 新环境-救援方案关系
MATCH (env6:Environment {id: 'env_006'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (env6)-[:SUITABLE_FOR {effectiveness: 0.75}]->(plan1)

MATCH (env7:Environment {id: 'env_007'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (env7)-[:SUITABLE_FOR {effectiveness: 0.80}]->(plan2)

MATCH (env8:Environment {id: 'env_008'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (env8)-[:SUITABLE_FOR {effectiveness: 0.70}]->(plan3)

MATCH (env9:Environment {id: 'env_009'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (env9)-[:SUITABLE_FOR {effectiveness: 0.85}]->(plan2)

MATCH (env10:Environment {id: 'env_010'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (env10)-[:SUITABLE_FOR {effectiveness: 0.80}]->(plan1)

// 新物品-救援方案关系
MATCH (item9:Item {id: 'item_009'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (item9)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan1)

MATCH (item10:Item {id: 'item_010'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (item10)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan1)

MATCH (item11:Item {id: 'item_011'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item11)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item12:Item {id: 'item_012'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item12)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item13:Item {id: 'item_013'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (item13)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan3)

MATCH (item14:Item {id: 'item_014'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (item14)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan1)

MATCH (item15:Item {id: 'item_015'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item15)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item16:Item {id: 'item_016'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item16)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item17:Item {id: 'item_017'}), (plan6:RescuePlan {id: 'plan_006'})
CREATE (item17)-[:REQUIRES_RESCUE_PLAN {priority: 'medium'}]->(plan6)

MATCH (item18:Item {id: 'item_018'}), (plan7:RescuePlan {id: 'plan_007'})
CREATE (item18)-[:REQUIRES_RESCUE_PLAN {priority: 'low'}]->(plan7)

MATCH (item19:Item {id: 'item_019'}), (plan8:RescuePlan {id: 'plan_008'})
CREATE (item19)-[:REQUIRES_RESCUE_PLAN {priority: 'low'}]->(plan8)

MATCH (item20:Item {id: 'item_020'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item20)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

// 补充重要物品节点
CREATE (item21:Item {
    id: 'item_021',
    name: '床垫',
    material: '泡沫',
    flammability: '极易燃',
    toxicity: '高',
    category: '家具',
    weight: '25kg',
    size: '200x150x20cm'
})

CREATE (item22:Item {
    id: 'item_022',
    name: '枕头',
    material: '泡沫',
    flammability: '极易燃',
    toxicity: '高',
    category: '家具',
    weight: '2kg',
    size: '60x40x15cm'
})

CREATE (item23:Item {
    id: 'item_023',
    name: '地毯',
    material: '纤维',
    flammability: '易燃',
    toxicity: '中',
    category: '装饰',
    weight: '15kg',
    size: '300x200x2cm'
})

CREATE (item24:Item {
    id: 'item_024',
    name: '窗帘',
    material: '布料',
    flammability: '易燃',
    toxicity: '中',
    category: '装饰',
    weight: '3kg',
    size: '300x200x1cm'
})

CREATE (item25:Item {
    id: 'item_025',
    name: '手机',
    material: '塑料',
    flammability: '易燃',
    toxicity: '高',
    category: '电器',
    weight: '0.2kg',
    size: '15x8x1cm'
})

CREATE (item26:Item {
    id: 'item_026',
    name: '笔记本电脑',
    material: '塑料',
    flammability: '易燃',
    toxicity: '高',
    category: '电器',
    weight: '2kg',
    size: '35x25x2cm'
})

CREATE (item27:Item {
    id: 'item_027',
    name: '音响',
    material: '塑料',
    flammability: '易燃',
    toxicity: '高',
    category: '电器',
    weight: '5kg',
    size: '30x20x15cm'
})

CREATE (item28:Item {
    id: 'item_028',
    name: '画作',
    material: '纸质',
    flammability: '极易燃',
    toxicity: '低',
    category: '装饰',
    weight: '1kg',
    size: '50x40x2cm'
})

CREATE (item29:Item {
    id: 'item_029',
    name: '植物',
    material: '有机',
    flammability: '易燃',
    toxicity: '低',
    category: '装饰',
    weight: '3kg',
    size: '30x30x50cm'
})

CREATE (item30:Item {
    id: 'item_030',
    name: '清洁剂',
    material: '液体',
    flammability: '易燃',
    toxicity: '高',
    category: '化学品',
    weight: '1kg',
    size: '20x10x30cm'
})

CREATE (item31:Item {
    id: 'item_031',
    name: '汽油',
    material: '液体',
    flammability: '极易燃',
    toxicity: '高',
    category: '化学品',
    weight: '5kg',
    size: '25x15x20cm'
})

CREATE (item32:Item {
    id: 'item_032',
    name: '氧气瓶',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '气体',
    weight: '15kg',
    size: '30x30x80cm'
})

CREATE (item33:Item {
    id: 'item_033',
    name: '液化气罐',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '气体',
    weight: '20kg',
    size: '35x35x60cm'
})

CREATE (item34:Item {
    id: 'item_034',
    name: '油漆',
    material: '液体',
    flammability: '易燃',
    toxicity: '高',
    category: '化学品',
    weight: '3kg',
    size: '20x15x25cm'
})

CREATE (item35:Item {
    id: 'item_035',
    name: '酒精',
    material: '液体',
    flammability: '极易燃',
    toxicity: '中',
    category: '化学品',
    weight: '1kg',
    size: '15x10x20cm'
})

// 补充重要材质节点
CREATE (material11:Material {
    id: 'material_011',
    name: '纤维',
    flammability_level: '高',
    toxicity_level: '中',
    ignition_point: 200,
    melting_point: null,
    density: '0.4g/cm³',
    description: '纤维材料，易燃且燃烧时产生有毒气体'
})

CREATE (material12:Material {
    id: 'material_012',
    name: '纸质',
    flammability_level: '极高',
    toxicity_level: '低',
    ignition_point: 150,
    melting_point: null,
    density: '0.8g/cm³',
    description: '纸质材料，极易燃且燃烧迅速'
})

CREATE (material13:Material {
    id: 'material_013',
    name: '有机',
    flammability_level: '高',
    toxicity_level: '低',
    ignition_point: 250,
    melting_point: null,
    density: '0.6g/cm³',
    description: '有机材料，易燃但毒性较低'
})

CREATE (material14:Material {
    id: 'material_014',
    name: '液体',
    flammability_level: '极高',
    toxicity_level: '高',
    ignition_point: 100,
    melting_point: null,
    density: '1.0g/cm³',
    description: '液体材料，极易燃且燃烧时产生大量有毒气体'
})

CREATE (material15:Material {
    id: 'material_015',
    name: '气体',
    flammability_level: '极高',
    toxicity_level: '低',
    ignition_point: 50,
    melting_point: null,
    density: '0.1g/cm³',
    description: '气体材料，极易燃且可能爆炸'
})

// 补充重要环境节点
CREATE (env11:Environment {
    id: 'env_011',
    name: '实验室',
    type: '室内',
    area: '科研',
    fire_characteristics: '化学品多，爆炸风险高',
    ventilation_level: '良好',
    evacuation_difficulty: '极高',
    floor_range: '多层',
    occupancy_density: '低'
})

CREATE (env12:Environment {
    id: 'env_012',
    name: '化工厂',
    type: '室内',
    area: '工业',
    fire_characteristics: '危险化学品多，爆炸风险极高',
    ventilation_level: '一般',
    evacuation_difficulty: '极高',
    floor_range: '单层',
    occupancy_density: '中等'
})

CREATE (env13:Environment {
    id: 'env_013',
    name: '加油站',
    type: '室外',
    area: '商业',
    fire_characteristics: '易燃液体多，爆炸风险极高',
    ventilation_level: '极好',
    evacuation_difficulty: '中等',
    floor_range: '地面',
    occupancy_density: '变化'
})

CREATE (env14:Environment {
    id: 'env_014',
    name: '机场',
    type: '室内',
    area: '交通',
    fire_characteristics: '人员密集，疏散复杂',
    ventilation_level: '良好',
    evacuation_difficulty: '高',
    floor_range: '多层',
    occupancy_density: '极高'
})

CREATE (env15:Environment {
    id: 'env_015',
    name: '地铁站',
    type: '地下',
    area: '交通',
    fire_characteristics: '地下空间，疏散困难',
    ventilation_level: '一般',
    evacuation_difficulty: '极高',
    floor_range: '地下',
    occupancy_density: '极高'
})

// 补充重要救援方案节点
CREATE (plan11:RescuePlan {
    id: 'plan_011',
    name: '泡沫床垫火灾救援',
    priority: '极紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有通风口',
        '使用干粉灭火器',
        '严禁使用水或泡沫',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '防护服', '安全绳'],
    warnings: [
        '泡沫材料燃烧极快',
        '产生大量有毒气体',
        '火势蔓延极快，难以控制'
    ],
    estimated_duration: 5,
    success_rate: 0.60
})

CREATE (plan12:RescuePlan {
    id: 'plan_012',
    name: '纸质材料火灾救援',
    priority: '紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有门窗',
        '使用干粉灭火器',
        '注意防止复燃',
        '如无法控制，立即撤离'
    ],
    equipment: ['干粉灭火器', '湿毛巾', '安全绳', '手电筒'],
    warnings: [
        '纸质材料燃烧极快',
        '火势蔓延迅速',
        '注意防止复燃'
    ],
    estimated_duration: 8,
    success_rate: 0.75
})

CREATE (plan13:RescuePlan {
    id: 'plan_013',
    name: '液体化学品火灾救援',
    priority: '极紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有通风口',
        '使用干粉灭火器',
        '严禁使用水扑救',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '防护服', '安全绳'],
    warnings: [
        '液体化学品燃烧极快',
        '产生大量有毒气体',
        '可能发生爆炸'
    ],
    estimated_duration: 5,
    success_rate: 0.50
})

CREATE (plan14:RescuePlan {
    id: 'plan_014',
    name: '气体泄漏火灾救援',
    priority: '极紧急',
    steps: [
        '立即疏散所有人员',
        '关闭气源',
        '严禁使用明火',
        '使用干粉灭火器',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '防护服', '安全绳'],
    warnings: [
        '气体泄漏可能爆炸',
        '严禁使用明火',
        '立即撤离危险区域'
    ],
    estimated_duration: 3,
    success_rate: 0.40
})

CREATE (plan15:RescuePlan {
    id: 'plan_015',
    name: '实验室火灾救援',
    priority: '极紧急',
    steps: [
        '立即疏散所有人员',
        '关闭所有设备',
        '使用干粉灭火器',
        '注意化学品反应',
        '立即撤离并报警'
    ],
    equipment: ['干粉灭火器', '防毒面具', '防护服', '安全绳'],
    warnings: [
        '实验室化学品多',
        '可能发生化学反应',
        '爆炸风险极高'
    ],
    estimated_duration: 8,
    success_rate: 0.45
})

// 补充关系
// 新物品-材质关系
MATCH (item21:Item {id: 'item_021'}), (material5:Material {id: 'material_005'})
CREATE (item21)-[:HAS_MATERIAL {strength: 'strong'}]->(material5)

MATCH (item22:Item {id: 'item_022'}), (material5:Material {id: 'material_005'})
CREATE (item22)-[:HAS_MATERIAL {strength: 'strong'}]->(material5)

MATCH (item23:Item {id: 'item_023'}), (material11:Material {id: 'material_011'})
CREATE (item23)-[:HAS_MATERIAL {strength: 'strong'}]->(material11)

MATCH (item24:Item {id: 'item_024'}), (material3:Material {id: 'material_003'})
CREATE (item24)-[:HAS_MATERIAL {strength: 'strong'}]->(material3)

MATCH (item25:Item {id: 'item_025'}), (material4:Material {id: 'material_004'})
CREATE (item25)-[:HAS_MATERIAL {strength: 'strong'}]->(material4)

MATCH (item26:Item {id: 'item_026'}), (material4:Material {id: 'material_004'})
CREATE (item26)-[:HAS_MATERIAL {strength: 'strong'}]->(material4)

MATCH (item27:Item {id: 'item_027'}), (material4:Material {id: 'material_004'})
CREATE (item27)-[:HAS_MATERIAL {strength: 'strong'}]->(material4)

MATCH (item28:Item {id: 'item_028'}), (material12:Material {id: 'material_012'})
CREATE (item28)-[:HAS_MATERIAL {strength: 'strong'}]->(material12)

MATCH (item29:Item {id: 'item_029'}), (material13:Material {id: 'material_013'})
CREATE (item29)-[:HAS_MATERIAL {strength: 'strong'}]->(material13)

MATCH (item30:Item {id: 'item_030'}), (material14:Material {id: 'material_014'})
CREATE (item30)-[:HAS_MATERIAL {strength: 'strong'}]->(material14)

MATCH (item31:Item {id: 'item_031'}), (material14:Material {id: 'material_014'})
CREATE (item31)-[:HAS_MATERIAL {strength: 'strong'}]->(material14)

MATCH (item32:Item {id: 'item_032'}), (material2:Material {id: 'material_002'})
CREATE (item32)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

MATCH (item33:Item {id: 'item_033'}), (material2:Material {id: 'material_002'})
CREATE (item33)-[:HAS_MATERIAL {strength: 'strong'}]->(material2)

MATCH (item34:Item {id: 'item_034'}), (material14:Material {id: 'material_014'})
CREATE (item34)-[:HAS_MATERIAL {strength: 'strong'}]->(material14)

MATCH (item35:Item {id: 'item_035'}), (material14:Material {id: 'material_014'})
CREATE (item35)-[:HAS_MATERIAL {strength: 'strong'}]->(material14)

// 新材质-救援方案关系
MATCH (material11:Material {id: 'material_011'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (material11)-[:REQUIRES_RESCUE_PLAN {applicability: 0.85}]->(plan3)

MATCH (material12:Material {id: 'material_012'}), (plan12:RescuePlan {id: 'plan_012'})
CREATE (material12)-[:REQUIRES_RESCUE_PLAN {applicability: 0.90}]->(plan12)

MATCH (material13:Material {id: 'material_013'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (material13)-[:REQUIRES_RESCUE_PLAN {applicability: 0.80}]->(plan1)

MATCH (material14:Material {id: 'material_014'}), (plan13:RescuePlan {id: 'plan_013'})
CREATE (material14)-[:REQUIRES_RESCUE_PLAN {applicability: 0.95}]->(plan13)

MATCH (material15:Material {id: 'material_015'}), (plan14:RescuePlan {id: 'plan_014'})
CREATE (material15)-[:REQUIRES_RESCUE_PLAN {applicability: 0.90}]->(plan14)

// 新环境-救援方案关系
MATCH (env11:Environment {id: 'env_011'}), (plan15:RescuePlan {id: 'plan_015'})
CREATE (env11)-[:SUITABLE_FOR {effectiveness: 0.85}]->(plan15)

MATCH (env12:Environment {id: 'env_012'}), (plan13:RescuePlan {id: 'plan_013'})
CREATE (env12)-[:SUITABLE_FOR {effectiveness: 0.90}]->(plan13)

MATCH (env13:Environment {id: 'env_013'}), (plan14:RescuePlan {id: 'plan_014'})
CREATE (env13)-[:SUITABLE_FOR {effectiveness: 0.95}]->(plan14)

MATCH (env14:Environment {id: 'env_014'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (env14)-[:SUITABLE_FOR {effectiveness: 0.75}]->(plan1)

MATCH (env15:Environment {id: 'env_015'}), (plan8:RescuePlan {id: 'plan_008'})
CREATE (env15)-[:SUITABLE_FOR {effectiveness: 0.70}]->(plan8)

// 新物品-救援方案关系
MATCH (item21:Item {id: 'item_021'}), (plan11:RescuePlan {id: 'plan_011'})
CREATE (item21)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan11)

MATCH (item22:Item {id: 'item_022'}), (plan11:RescuePlan {id: 'plan_011'})
CREATE (item22)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan11)

MATCH (item23:Item {id: 'item_023'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (item23)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan3)

MATCH (item24:Item {id: 'item_024'}), (plan3:RescuePlan {id: 'plan_003'})
CREATE (item24)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan3)

MATCH (item25:Item {id: 'item_025'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item25)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item26:Item {id: 'item_026'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item26)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item27:Item {id: 'item_027'}), (plan2:RescuePlan {id: 'plan_002'})
CREATE (item27)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan2)

MATCH (item28:Item {id: 'item_028'}), (plan12:RescuePlan {id: 'plan_012'})
CREATE (item28)-[:REQUIRES_RESCUE_PLAN {priority: 'urgent'}]->(plan12)

MATCH (item29:Item {id: 'item_029'}), (plan1:RescuePlan {id: 'plan_001'})
CREATE (item29)-[:REQUIRES_RESCUE_PLAN {priority: 'high'}]->(plan1)

MATCH (item30:Item {id: 'item_030'}), (plan13:RescuePlan {id: 'plan_013'})
CREATE (item30)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan13)

MATCH (item31:Item {id: 'item_031'}), (plan13:RescuePlan {id: 'plan_013'})
CREATE (item31)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan13)

MATCH (item32:Item {id: 'item_032'}), (plan14:RescuePlan {id: 'plan_014'})
CREATE (item32)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan14)

MATCH (item33:Item {id: 'item_033'}), (plan14:RescuePlan {id: 'plan_014'})
CREATE (item33)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan14)

MATCH (item34:Item {id: 'item_034'}), (plan13:RescuePlan {id: 'plan_013'})
CREATE (item34)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan13)

MATCH (item35:Item {id: 'item_035'}), (plan13:RescuePlan {id: 'plan_013'})
CREATE (item35)-[:REQUIRES_RESCUE_PLAN {priority: 'critical'}]->(plan13);

// 注意：索引将在数据导入后单独创建
