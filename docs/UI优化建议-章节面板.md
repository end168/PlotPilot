# 章节状态和章节元素面板优化建议

## 📋 当前问题分析

### 1. 章节状态面板
- **信息密集**：太多卡片堆叠，视觉层次不清晰
- **重复内容**：「人工审阅」和「全托管章末审阅」功能重复
- **AI审阅功能不明确**：用户提到的"AI审阅包括检查多项，包括ai率，一致性等"应该更突出

### 2. 章节元素面板  
- **节拍展示不够清晰**：当前只显示一层节拍
- **信息冗余**：「本章规划」「节拍」「本章总结」有重复内容

## 🎨 优化方案

### 方案一：保持现有Tab结构，优化视觉效果

```
┌─────────────────────────────────────────────────────────┐
│  📋 章节状态                                              │
├─────────────────────────────────────────────────────────┤
│  【本章概览】 - 一行卡片                                   │
│  第 X 章 | 标题 | 字数 | 状态                             │
├─────────────────────────────────────────────────────────┤
│  【AI 审阅报告】⭐ 核心功能                                │
│  ┌─────────────────────────────────────────────┐        │
│  │ ✅ AI 率检测: 8.5% (优秀)                    │        │
│  │ ✅ 一致性检查: 通过                          │        │
│  │ ⚠️  节奏分析: 偏慢                          │        │
│  │ ℹ️  张力值: 4/10 (平缓)                     │        │
│  │                                              │        │
│  │ 【展开详情】查看完整报告...                  │        │
│  └─────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────┤
│  【人工审阅】                                              │
│  状态: [已审] 备忘: [文本框]                               │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│  🧩 章节元素                                              │
├─────────────────────────────────────────────────────────┤
│  【本章规划】                                              │
│  标题: XXX                                                │
│  视角: 陈默                                               │
│  时间线: 第1天 → 第3天                                    │
├─────────────────────────────────────────────────────────┤
│  【节拍规划】⭐ 双层展示                                   │
│  ┌─────────────────────────────────────────────┐        │
│  │ 🎬 宏观节拍 (来自大纲)                       │        │
│  │ 1. 警方黄sir接到报案...                     │        │
│  │ 2. 搜救队发现奇怪痕迹...                     │        │
│  │ 3. 黄sir联系中大...                          │        │
│  │                                              │        │
│  │ 🎭 微观节拍 (写作时放大)                     │        │
│  │ Beat 1: 场景开场 (800字, 感官)              │        │
│  │ Beat 2: 主要事件 (1200字, 对话)             │        │
│  │ Beat 3: 场景收尾 (500字, 情绪)              │        │
│  └─────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────┤
│  【本章总结】                                              │
│  摘要: ...                                                │
│  关键事件: ...                                            │
└─────────────────────────────────────────────────────────┘
```

### 方案二：拆分为更多Tab（如果内容很多）

```
【本章概览】【节拍规划】【AI审阅】【元素关联】

Tab 1 - 本章概览
- 章节基本信息
- 本章规划（标题、大纲、视角）
- 本章总结

Tab 2 - 节拍规划
- 宏观节拍列表
- 微观节拍列表（如果有）
- 节拍执行进度

Tab 3 - AI审阅
- AI率检测
- 一致性报告
- 张力分析
- 文风相似度
- 漂移告警

Tab 4 - 元素关联
- 人物
- 地点
- 道具
- 伏笔建议
```

## 💡 具体优化建议

### 1. 节拍展示优化

```vue
<n-card title="节拍规划" size="small" :bordered="true" class="ce-card-beats">
  <n-tabs type="segment" size="small">
    <n-tab-pane name="macro" tab="🎬 宏观节拍">
      <n-text depth="3" style="font-size: 12px; margin-bottom: 8px; display: block">
        来自章节大纲，用于叙事摘要和向量检索
      </n-text>
      <ol class="ce-beat-list">
        <li v-for="(beat, i) in macroBeats" :key="i">{{ beat }}</li>
      </ol>
    </n-tab-pane>
    
    <n-tab-pane name="micro" tab="🎭 微观节拍">
      <n-text depth="3" style="font-size: 12px; margin-bottom: 8px; display: block">
        写作时智能拆分，控制节奏和感官细节
      </n-text>
      <n-space vertical :size="8">
        <div v-for="(beat, i) in microBeats" :key="i" class="micro-beat-item">
          <n-tag :type="getBeatType(beat.focus)" size="small">
            {{ beat.focus }}
          </n-tag>
          <n-text strong style="margin: 0 8px">Beat {{ i + 1 }}</n-text>
          <n-text depth="3" style="font-size: 12px">
            ({{ beat.target_words }}字)
          </n-text>
          <div style="margin-top: 4px; font-size: 13px">
            {{ beat.description }}
          </div>
        </div>
      </n-space>
    </n-tab-pane>
  </n-tabs>
</n-card>
```

### 2. AI审阅报告优化

```vue
<n-card title="AI 审阅报告" size="small" :bordered="true">
  <n-space vertical :size="12">
    <!-- 核心指标 -->
    <n-grid :cols="2" :x-gap="12" :y-gap="12">
      <n-gi>
        <n-statistic label="AI率" :value="aiRate">
          <template #suffix>%</template>
          <template #prefix>
            <n-tag :type="aiRate < 15 ? 'success' : 'warning'" size="small">
              {{ aiRate < 15 ? '优秀' : '需优化' }}
            </n-tag>
          </template>
        </n-statistic>
      </n-gi>
      <n-gi>
        <n-statistic label="张力值" :value="tensionScore">
          <template #suffix>/ 10</template>
        </n-statistic>
      </n-gi>
    </n-grid>
    
    <!-- 详细报告 -->
    <n-collapse>
      <n-collapse-item title="一致性检查详情" name="consistency">
        <ConsistencyReportPanel :report="consistencyReport" />
      </n-collapse-item>
      <n-collapse-item title="文风分析" name="style">
        <n-descriptions :column="1" size="small">
          <n-descriptions-item label="相似度">
            {{ styleSimilarity }}
          </n-descriptions-item>
          <n-descriptions-item label="漂移告警">
            <n-tag :type="driftAlert ? 'error' : 'success'" size="small">
              {{ driftAlert ? '是' : '否' }}
            </n-tag>
          </n-descriptions-item>
        </n-descriptions>
      </n-collapse-item>
    </n-collapse>
  </n-space>
</n-card>
```

### 3. 样式优化

```css
/* 卡片间距优化 */
.ce-panel .n-card {
  margin-bottom: 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.ce-panel .n-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* 节拍列表优化 */
.ce-beat-list {
  margin: 8px 0;
  padding-left: 1.5rem;
  line-height: 1.8;
  color: var(--n-text-color-2);
}

.ce-beat-list li {
  margin-bottom: 6px;
  padding-left: 4px;
  border-left: 2px solid var(--n-border-color);
  transition: border-color 0.2s;
}

.ce-beat-list li:hover {
  border-left-color: var(--n-primary-color);
}

/* 微观节拍项 */
.micro-beat-item {
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--n-color-modal);
  border: 1px solid var(--n-border-color);
  transition: all 0.2s;
}

.micro-beat-item:hover {
  border-color: var(--n-primary-color);
  background: rgba(99, 102, 241, 0.02);
}
```

## 🎯 推荐方案

基于当前代码复杂度和用户体验，我推荐：

1. **保持现有Tab结构**（不拆分更多Tab）
2. **优化节拍展示**：增加宏观/微观Tab切换
3. **增强AI审阅**：增加核心指标卡片，使用折叠面板展示详情
4. **改进视觉层次**：使用间距、颜色、图标区分重要程度

## 📊 优先级

1. **高优先级**：节拍双层展示（用户明确提到）
2. **中优先级**：AI审阅报告优化
3. **低优先级**：细节样式美化

## 🚀 实施步骤

1. 先实现节拍双层展示（宏观+微观）
2. 优化AI审阅报告布局
3. 最后调整样式细节

---

**注意**：这些建议需要根据实际API数据结构调整，特别是微观节拍需要从守护进程日志中提取。
