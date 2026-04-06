<template>
  <div class="ce-panel">
    <n-empty v-if="!currentChapterNumber" description="请先从左侧选择一个章节" style="margin-top: 40px" />

    <template v-else>
      <n-scrollbar class="ce-scroll">
        <n-space vertical :size="12" style="padding-bottom: 16px">
          <n-alert v-if="readOnly" type="warning" :show-icon="true" style="font-size: 12px">
            托管运行中：仅可查看，不可增删元素关联。
          </n-alert>

          <n-card
            v-if="autopilotChapterReview && currentChapterNumber === autopilotChapterReview.chapter_number"
            title="全托管 · 本章管线摘要"
            size="small"
            :bordered="true"
          >
            <n-space vertical :size="6">
              <n-text depth="3" style="font-size: 12px">
                与「📋 章节状态」审阅同源：结构树元素关联仍以下方列表为准；管线侧已写入叙事知识、向量检索、三元组与伏笔账本（右栏可刷新查看）。
              </n-text>
              <n-descriptions :column="1" label-placement="left" size="small">
                <n-descriptions-item label="张力">{{ autopilotChapterReview.tension }} / 10</n-descriptions-item>
                <n-descriptions-item label="叙事同步">
                  <n-tag
                    :type="autopilotChapterReview.narrative_sync_ok ? 'success' : 'warning'"
                    size="tiny"
                    round
                  >
                    {{ autopilotChapterReview.narrative_sync_ok ? '已落库' : '异常' }}
                  </n-tag>
                </n-descriptions-item>
                <n-descriptions-item label="文风">
                  {{
                    autopilotChapterReview.similarity_score != null
                      ? Number(autopilotChapterReview.similarity_score).toFixed(3)
                      : '—'
                  }}
                  ·
                  <n-tag
                    :type="autopilotChapterReview.drift_alert ? 'error' : 'default'"
                    size="tiny"
                    round
                  >
                    {{ autopilotChapterReview.drift_alert ? '漂移告警' : '正常' }}
                  </n-tag>
                </n-descriptions-item>
              </n-descriptions>
            </n-space>
          </n-card>

          <!-- 本章规划（结构树节点：节拍/大纲/视角等） -->
          <n-card v-if="chapterPlan" title="本章规划（结构树）" size="small" :bordered="true" class="ce-card-plan">
            <n-space vertical :size="8">
              <n-text depth="3" class="ce-card-lead">
                与左侧「宏观规划」同源；写作前对齐标题、大纲节拍与 POV。下方「伏笔建议」空时可沿用此处大纲做匹配。
              </n-text>
              <n-descriptions :column="1" label-placement="left" size="small" label-style="white-space: nowrap">
                <n-descriptions-item label="标题">{{ chapterPlan.title || '—' }}</n-descriptions-item>
                <n-descriptions-item v-if="chapterPlan.outline" label="大纲（全文）">
                  <n-text style="font-size: 12px; white-space: pre-wrap">{{ chapterPlan.outline }}</n-text>
                </n-descriptions-item>
                <n-descriptions-item v-if="chapterPlan.description" label="结构树摘要">
                  <n-text style="font-size: 12px; white-space: pre-wrap">{{ chapterPlan.description }}</n-text>
                </n-descriptions-item>
                <n-descriptions-item v-if="chapterPlan.pov_character_id" label="视角 POV">
                  {{ chapterPlan.pov_character_id }}
                </n-descriptions-item>
                <n-descriptions-item
                  v-if="chapterPlan.timeline_start || chapterPlan.timeline_end"
                  label="时间线"
                >
                  {{ chapterPlan.timeline_start || '—' }} → {{ chapterPlan.timeline_end || '—' }}
                </n-descriptions-item>
                <n-descriptions-item v-if="planMoodLine" label="情绪 / 基调">
                  {{ planMoodLine }}
                </n-descriptions-item>
              </n-descriptions>
            </n-space>
          </n-card>

          <n-card
            v-if="currentChapterNumber && showBeatsCard"
            title="节拍规划"
            size="small"
            :bordered="true"
            class="ce-card-beats"
          >
            <n-tabs type="segment" size="small" animated>
              <n-tab-pane name="macro" tab="🎬 宏观节拍">
                <n-text depth="3" class="ce-card-lead">
                  来自章节大纲，用于叙事摘要和向量检索
                </n-text>
                <ol v-if="beatLines.length" class="ce-beat-list">
                  <li v-for="(line, bi) in beatLines" :key="bi">{{ line }}</li>
                </ol>
                <n-empty v-else description="暂无宏观节拍；可在叙事知识中为本章填写 beat_sections，或在结构树大纲用多行书写" size="small" />
              </n-tab-pane>
              
              <n-tab-pane name="micro" tab="🎭 微观节拍">
                <n-text depth="3" class="ce-card-lead">
                  写作时智能拆分，控制节奏和感官细节（来自守护进程日志）
                </n-text>
                <n-space v-if="microBeats.length" vertical :size="8" style="margin-top: 12px">
                  <div v-for="(beat, i) in microBeats" :key="i" class="micro-beat-item">
                    <div class="micro-beat-header">
                      <n-tag :type="getBeatTypeColor(beat.focus)" size="small" round>
                        {{ beat.focus }}
                      </n-tag>
                      <n-text strong style="margin-left: 8px">Beat {{ i + 1 }}</n-text>
                      <n-text depth="3" style="margin-left: 8px; font-size: 12px">
                        ({{ beat.target_words }}字)
                      </n-text>
                    </div>
                    <div class="micro-beat-desc">
                      {{ beat.description }}
                    </div>
                  </div>
                </n-space>
                <n-empty v-else description="微观节拍在章节生成时自动创建，当前章节暂无数据" size="small" />
              </n-tab-pane>
            </n-tabs>
          </n-card>

          <n-card
            v-if="currentChapterNumber && hasSummaryBlock"
            title="本章总结"
            size="small"
            :bordered="true"
            class="ce-card-summary"
          >
            <n-text v-if="summarySourceHint" depth="3" class="ce-card-lead">{{ summarySourceHint }}</n-text>
            <n-descriptions
              v-if="knowledgeChapter && (knowledgeChapter.summary || knowledgeChapter.key_events || knowledgeChapter.consistency_note)"
              :column="1"
              label-placement="left"
              size="small"
            >
              <n-descriptions-item v-if="knowledgeChapter.summary" label="摘要">
                <n-text style="font-size: 12px; white-space: pre-wrap">{{ knowledgeChapter.summary }}</n-text>
              </n-descriptions-item>
              <n-descriptions-item v-if="knowledgeChapter.key_events" label="关键事件">
                <n-text style="font-size: 12px; white-space: pre-wrap">{{ knowledgeChapter.key_events }}</n-text>
              </n-descriptions-item>
              <n-descriptions-item v-if="knowledgeChapter.consistency_note" label="一致性备注">
                <n-text style="font-size: 12px; white-space: pre-wrap">{{ knowledgeChapter.consistency_note }}</n-text>
              </n-descriptions-item>
            </n-descriptions>
            <n-text
              v-else-if="chapterPlan?.description"
              style="font-size: 12px; white-space: pre-wrap; line-height: 1.55"
            >
              {{ chapterPlan.description }}
            </n-text>
            <n-text depth="3" class="ce-k-hint">
              叙事知识来自 <code class="ce-inline-code">GET /novels/{id}/knowledge</code> 中与本章号对应的章节条目。
            </n-text>
          </n-card>

          <n-alert v-else-if="storyNodeNotFound" type="warning" :show-icon="true">
            未在结构树中找到第 {{ currentChapterNumber }} 章的规划节点。请先在左侧「宏观规划」中创建章节结构；创建后此处将显示本章大纲、视角等，并支持下方元素关联。
          </n-alert>

          <!-- 元素关联 -->
          <n-card size="small" :bordered="true" class="ce-card-elements">
            <template #header>
              <div class="ce-card-header-col">
                <span class="ce-card-header-title">人物 / 地点 / 道具（章级）</span>
                <n-text depth="3" class="ce-card-header-sub">
                  与 Bible 元素 ID 一致，供本章检索、批注与叙事同步；非全书设定。
                </n-text>
              </div>
            </template>
            <template #header-extra>
              <n-space :size="6">
                <n-select
                  v-model:value="filterType"
                  :options="elementTypeOptions"
                  size="tiny"
                  style="width: 90px"
                  clearable
                  placeholder="类型"
                  @update:value="loadElements"
                />
                <n-button size="tiny" secondary :loading="loading" @click="loadElements">刷新</n-button>
              </n-space>
            </template>

            <n-spin :show="loading">
              <n-space vertical :size="5">
                <n-space v-if="groupedCharacters.length" vertical :size="4">
                  <n-text strong class="ce-group-label">人物</n-text>
                  <div v-for="elem in groupedCharacters" :key="elem.id" class="ce-item">
                    <div class="ce-item-info">
                      <n-text class="ce-id">{{ elem.element_id }}</n-text>
                      <n-tag size="tiny" round>{{ relationLabel(elem.relation_type) }}</n-tag>
                      <n-tag :type="elem.importance === 'major' ? 'error' : elem.importance === 'minor' ? 'default' : 'info'" size="tiny" round>
                        {{ importanceLabel(elem.importance) }}
                      </n-tag>
                      <n-text v-if="elem.notes" depth="3" class="ce-notes ce-notes--inline">{{ elem.notes }}</n-text>
                    </div>
                    <n-button
                      v-if="!readOnly"
                      size="tiny"
                      type="error"
                      text
                      :loading="deletingId === elem.id"
                      @click="doDelete(elem)"
                    >删除</n-button>
                  </div>
                </n-space>

                <n-space v-if="groupedLocations.length" vertical :size="4">
                  <n-text strong class="ce-group-label">地点</n-text>
                  <div v-for="elem in groupedLocations" :key="elem.id" class="ce-item">
                    <div class="ce-item-info">
                      <n-text class="ce-id">{{ elem.element_id }}</n-text>
                      <n-tag size="tiny" round>{{ relationLabel(elem.relation_type) }}</n-tag>
                      <n-tag :type="elem.importance === 'major' ? 'error' : elem.importance === 'minor' ? 'default' : 'info'" size="tiny" round>
                        {{ importanceLabel(elem.importance) }}
                      </n-tag>
                      <n-text v-if="elem.notes" depth="3" class="ce-notes ce-notes--inline">{{ elem.notes }}</n-text>
                    </div>
                    <n-button
                      v-if="!readOnly"
                      size="tiny"
                      type="error"
                      text
                      :loading="deletingId === elem.id"
                      @click="doDelete(elem)"
                    >删除</n-button>
                  </div>
                </n-space>

                <n-space v-if="groupedOther.length" vertical :size="4">
                  <n-text strong class="ce-group-label">其他</n-text>
                  <div v-for="elem in groupedOther" :key="elem.id" class="ce-item">
                    <div class="ce-item-info">
                      <n-tag :type="elemTypeColor(elem.element_type)" size="tiny" round>{{ elemTypeLabel(elem.element_type) }}</n-tag>
                      <n-text class="ce-id ce-id--inline">{{ elem.element_id }}</n-text>
                      <n-tag size="tiny" round>{{ relationLabel(elem.relation_type) }}</n-tag>
                      <n-tag :type="elem.importance === 'major' ? 'error' : elem.importance === 'minor' ? 'default' : 'info'" size="tiny" round>
                        {{ importanceLabel(elem.importance) }}
                      </n-tag>
                      <n-text v-if="elem.notes" depth="3" class="ce-notes">{{ elem.notes }}</n-text>
                    </div>
                    <n-button
                      v-if="!readOnly"
                      size="tiny"
                      type="error"
                      text
                      :loading="deletingId === elem.id"
                      @click="doDelete(elem)"
                    >删除</n-button>
                  </div>
                </n-space>

                <n-empty v-if="!loading && elements.length === 0 && !storyNodeNotFound" description="暂无关联元素" />
              </n-space>
            </n-spin>

            <n-card
              v-if="storyNodeId && !storyNodeNotFound && !readOnly"
              title="添加元素关联"
              size="small"
              :bordered="false"
              style="margin-top: 10px; border-top: 1px solid var(--n-divider-color, rgba(0,0,0,.07))"
            >
              <n-space vertical :size="8">
                <n-space :size="6" wrap>
                  <n-select
                    v-model:value="form.element_type"
                    :options="elementTypeOptions"
                    size="small"
                    style="width: 90px"
                    placeholder="类型"
                  />
                  <n-input
                    v-model:value="form.element_id"
                    size="small"
                    placeholder="元素 ID（人物/地点名称）"
                    style="flex: 1; min-width: 120px"
                  />
                </n-space>
                <n-space :size="6" wrap>
                  <n-select
                    v-model:value="form.relation_type"
                    :options="relationTypeOptions"
                    size="small"
                    style="width: 100px"
                    placeholder="关联类型"
                  />
                  <n-select
                    v-model:value="form.importance"
                    :options="importanceOptions"
                    size="small"
                    style="width: 80px"
                    placeholder="重要性"
                  />
                  <n-input
                    v-model:value="form.notes"
                    size="small"
                    placeholder="备注（可选）"
                    style="flex: 1; min-width: 80px"
                  />
                </n-space>
                <n-button
                  type="primary"
                  size="small"
                  :loading="adding"
                  :disabled="!form.element_type || !form.element_id || !form.relation_type"
                  @click="doAdd"
                >
                  添加关联
                </n-button>
              </n-space>
            </n-card>
          </n-card>

          <!-- 片场：本章伏笔回收建议（原右侧「片场 → 本章建议」） -->
          <n-card title="片场 · 本章伏笔回收建议" size="small" :bordered="true">
            <ForeshadowChapterSuggestionsPanel
              :slug="slug"
              :current-chapter-number="currentChapterNumber"
              :prefill-outline="chapterPlan?.outline || ''"
              embedded
              compact
            />
          </n-card>

          <!-- AI 审阅与质检（与「章节状态」同源，便于编辑时对照） -->
          <n-card
            v-if="lastWorkflowResult && qcChapterNumber != null"
            title="AI 审阅与质检（最近一次流式生成）"
            size="small"
            :bordered="true"
          >
            <n-space vertical :size="10">
              <n-alert
                v-if="currentChapterNumber !== qcChapterNumber"
                type="info"
                :show-icon="true"
                style="font-size: 12px"
              >
                以下为针对「第 {{ qcChapterNumber }} 章」的质检；当前浏览第 {{ currentChapterNumber }} 章时可作参考。
              </n-alert>
              <ConsistencyReportPanel
                :report="lastWorkflowResult.consistency_report"
                :token-count="lastWorkflowResult.token_count"
                @location-click="onLocationClick"
              />
              <n-collapse
                v-if="lastWorkflowResult.style_warnings && lastWorkflowResult.style_warnings.length > 0"
                class="cliche-collapse"
              >
                <n-collapse-item
                  :title="`俗套句式命中 ${lastWorkflowResult.style_warnings.length} 处`"
                  name="cliche"
                >
                  <n-space vertical :size="6">
                    <n-alert
                      v-for="(w, i) in lastWorkflowResult.style_warnings"
                      :key="i"
                      :type="w.severity === 'warning' ? 'warning' : 'info'"
                      :title="w.pattern"
                      style="font-size: 12px"
                    >
                      「{{ w.text }}」
                    </n-alert>
                  </n-space>
                </n-collapse-item>
              </n-collapse>
              <n-text depth="3" style="font-size: 11px">
                完整本章概览与清除摘要见「📋 章节状态」Tab。
              </n-text>
            </n-space>
          </n-card>
        </n-space>
      </n-scrollbar>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useWorkbenchRefreshStore } from '../../stores/workbenchRefreshStore'
import { useMessage } from 'naive-ui'
import { chapterElementApi } from '../../api/chapterElement'
import type { ChapterElementDTO, ElementType, RelationType, Importance } from '../../api/chapterElement'
import { planningApi } from '../../api/planning'
import type { StoryNode } from '../../api/planning'
import { knowledgeApi } from '../../api/knowledge'
import type { ChapterSummary } from '../../api/knowledge'
import type { GenerateChapterWorkflowResponse } from '../../api/workflow'
import type { AutopilotChapterAudit } from './ChapterStatusPanel.vue'
import ForeshadowChapterSuggestionsPanel from './ForeshadowChapterSuggestionsPanel.vue'
import ConsistencyReportPanel from './ConsistencyReportPanel.vue'

const props = withDefaults(
  defineProps<{
    slug: string
    currentChapterNumber?: number | null
    /** 托管运行时只读，不可增删元素 */
    readOnly?: boolean
    /** 与章节状态 Tab 一致的最近一次生成质检（可选展示） */
    lastWorkflowResult?: GenerateChapterWorkflowResponse | null
    qcChapterNumber?: number | null
    autopilotChapterReview?: AutopilotChapterAudit | null
  }>(),
  {
    currentChapterNumber: null,
    readOnly: false,
    lastWorkflowResult: null,
    qcChapterNumber: null,
    autopilotChapterReview: null,
  }
)

const message = useMessage()

const elements = ref<ChapterElementDTO[]>([])
const loading = ref(false)
const adding = ref(false)
const deletingId = ref<string | null>(null)
const storyNodeId = ref<string | null>(null)
const storyNodeNotFound = ref(false)
const chapterPlan = ref<StoryNode | null>(null)
/** 叙事知识中与本章号对应的章节条目（节拍 / 摘要） */
const knowledgeChapter = ref<ChapterSummary | null>(null)
const filterType = ref<ElementType | undefined>(undefined)

const form = ref<{
  element_type: ElementType | undefined
  element_id: string
  relation_type: RelationType | undefined
  importance: Importance
  notes: string
}>({ element_type: undefined, element_id: '', relation_type: undefined, importance: 'normal', notes: '' })

const elementTypeOptions = [
  { label: '人物', value: 'character' },
  { label: '地点', value: 'location' },
  { label: '道具', value: 'item' },
  { label: '组织', value: 'organization' },
  { label: '事件', value: 'event' },
]

const relationTypeOptions = [
  { label: '出场', value: 'appears' },
  { label: '提及', value: 'mentioned' },
  { label: '场景', value: 'scene' },
  { label: '使用', value: 'uses' },
  { label: '参与', value: 'involved' },
  { label: '发生', value: 'occurs' },
]

const importanceOptions = [
  { label: '主要', value: 'major' },
  { label: '一般', value: 'normal' },
  { label: '次要', value: 'minor' },
]

const elemTypeLabel = (t: string) => elementTypeOptions.find(o => o.value === t)?.label ?? t
const elemTypeColor = (t: string): 'error' | 'warning' | 'info' | 'success' | 'default' => {
  const map: Record<string, 'error' | 'warning' | 'info' | 'success' | 'default'> = {
    character: 'error', location: 'success', item: 'warning', organization: 'info', event: 'default'
  }
  return map[t] ?? 'default'
}
const importanceLabel = (i: string) => importanceOptions.find(o => o.value === i)?.label ?? i
const relationLabel = (r: string) => relationTypeOptions.find(o => o.value === r)?.label ?? r

const groupedCharacters = computed(() =>
  elements.value.filter(e => e.element_type === 'character')
)
const groupedLocations = computed(() =>
  elements.value.filter(e => e.element_type === 'location')
)
const groupedOther = computed(() =>
  elements.value.filter(e => e.element_type !== 'character' && e.element_type !== 'location')
)

const planMoodLine = computed(() => {
  const m = chapterPlan.value?.metadata
  if (!m || typeof m !== 'object') return ''
  const mood = m.mood ?? m.emotion ?? m.tone
  if (typeof mood === 'string' && mood.trim()) return mood
  if (Array.isArray(m.moods) && m.moods.length) return m.moods.join('、')
  return ''
})

const beatLines = computed(() => {
  const k = knowledgeChapter.value
  if (k?.beat_sections?.length) {
    return k.beat_sections.map(s => String(s || '').trim()).filter(Boolean)
  }
  const ol = chapterPlan.value?.outline?.trim()
  if (!ol) return []
  return ol.split(/\n+/).map(s => s.trim()).filter(s => s.length > 0)
})

const showBeatsCard = computed(() => {
  if (!props.currentChapterNumber) return false
  if (beatLines.value.length > 0) return true
  return !!(chapterPlan.value?.outline?.trim() || knowledgeChapter.value)
})

const beatSourceHint = computed(() => {
  if (knowledgeChapter.value?.beat_sections?.length) {
    return '优先使用叙事知识库中的 beat_sections（章后管线落库后可见）。'
  }
  if (chapterPlan.value?.outline?.trim()) {
    return '当前无 beat_sections 时，将结构树大纲按行拆成节拍列表。'
  }
  return ''
})

// 微观节拍数据结构
interface MicroBeat {
  description: string
  target_words: number
  focus: string // 'sensory' | 'dialogue' | 'action' | 'emotion'
}

// TODO: 从守护进程日志或API获取微观节拍数据
// 当前使用模拟数据，实际需要从后端API获取
const microBeats = ref<MicroBeat[]>([])

// 根据focus类型返回标签颜色
const getBeatTypeColor = (focus: string): 'success' | 'warning' | 'error' | 'info' | 'default' => {
  const colorMap: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
    sensory: 'info',      // 感官 - 蓝色
    dialogue: 'success',  // 对话 - 绿色
    action: 'warning',    // 动作 - 黄色
    emotion: 'error',     // 情绪 - 红色
  }
  return colorMap[focus] || 'default'
}

const hasSummaryBlock = computed(() => {
  if (!props.currentChapterNumber) return false
  const k = knowledgeChapter.value
  if (k && (k.summary?.trim() || k.key_events?.trim() || k.consistency_note?.trim())) return true
  return !!chapterPlan.value?.description?.trim()
})

const summarySourceHint = computed(() => {
  const k = knowledgeChapter.value
  if (k && (k.summary?.trim() || k.key_events?.trim() || k.consistency_note?.trim())) {
    return '以下为叙事知识库中本章条目（与右栏知识库同源）。'
  }
  return '暂无叙事知识条目时，展示结构树「摘要」作为参考。'
})

/** 在结构树森林中按章节号查找 chapter 节点 */
function findChapterNode(nodes: StoryNode[], num: number): StoryNode | null {
  for (const node of nodes) {
    if (node.node_type === 'chapter' && node.number === num) return node
    if (node.children?.length) {
      const found = findChapterNode(node.children, num)
      if (found) return found
    }
  }
  return null
}

const resolveStoryNode = async () => {
  storyNodeId.value = null
  chapterPlan.value = null
  storyNodeNotFound.value = false
  if (!props.currentChapterNumber) return
  try {
    const res = await planningApi.getStructure(props.slug)
    const roots = res.data?.nodes ?? []
    const node = findChapterNode(roots, props.currentChapterNumber)
    if (node) {
      storyNodeId.value = node.id
      chapterPlan.value = node
    } else {
      storyNodeNotFound.value = true
    }
  } catch {
    storyNodeNotFound.value = true
  }
}

async function loadKnowledgeChapter() {
  knowledgeChapter.value = null
  if (!props.slug || !props.currentChapterNumber) return
  try {
    const k = await knowledgeApi.getKnowledge(props.slug)
    const row = k.chapters?.find(c => c.chapter_id === props.currentChapterNumber)
    knowledgeChapter.value = row ?? null
  } catch {
    knowledgeChapter.value = null
  }
}

const loadElements = async () => {
  if (!storyNodeId.value) return
  loading.value = true
  try {
    const res = await chapterElementApi.getElements(storyNodeId.value, filterType.value)
    elements.value = res.data
  } catch {
    message.error('加载章节元素失败')
  } finally {
    loading.value = false
  }
}

const doAdd = async () => {
  if (!storyNodeId.value || !form.value.element_type || !form.value.element_id || !form.value.relation_type) return
  adding.value = true
  try {
    const res = await chapterElementApi.addElement(storyNodeId.value, {
      element_type: form.value.element_type,
      element_id: form.value.element_id,
      relation_type: form.value.relation_type,
      importance: form.value.importance,
      notes: form.value.notes || undefined,
    })
    elements.value.push(res.data)
    form.value.element_id = ''
    form.value.notes = ''
    message.success('已添加')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    message.error(err?.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

const doDelete = async (elem: ChapterElementDTO) => {
  if (!storyNodeId.value) return
  deletingId.value = elem.id
  try {
    await chapterElementApi.deleteElement(storyNodeId.value, elem.id)
    elements.value = elements.value.filter(e => e.id !== elem.id)
    message.success('已删除')
  } catch {
    message.error('删除失败')
  } finally {
    deletingId.value = null
  }
}

function onLocationClick(location: number) {
  message.info(`问题位置约在第 ${location} 字附近，可在章节编辑中搜索或滚动查看。`)
}

watch(() => props.slug, async (slug) => {
  if (slug) {
    elements.value = []
    storyNodeId.value = null
    chapterPlan.value = null
    storyNodeNotFound.value = false
    await resolveStoryNode()
    await loadKnowledgeChapter()
    await loadElements()
  }
})

watch(() => props.currentChapterNumber, async () => {
  await resolveStoryNode()
  await loadKnowledgeChapter()
  await loadElements()
}, { immediate: false })

const refreshStore = useWorkbenchRefreshStore()
const { deskTick } = storeToRefs(refreshStore)
watch(deskTick, async () => {
  await resolveStoryNode()
  await loadKnowledgeChapter()
  await loadElements()
})

onMounted(async () => {
  await resolveStoryNode()
  await loadKnowledgeChapter()
  await loadElements()
})
</script>

<style scoped>
.ce-panel {
  padding: 0;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.ce-scroll {
  flex: 1;
  min-height: 0;
}

/* 微观节拍样式 */
.micro-beat-item {
  padding: 12px 14px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.04) 0%, rgba(139, 92, 246, 0.02) 100%);
  border: 1px solid rgba(99, 102, 241, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.micro-beat-item:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(139, 92, 246, 0.04) 100%);
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.08);
}

.micro-beat-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.micro-beat-desc {
  margin-top: 6px;
  padding-left: 4px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--n-text-color-2);
  border-left: 2px solid var(--n-border-color);
  padding-left: 12px;
}

.micro-beat-item:hover .micro-beat-desc {
  border-left-color: var(--n-primary-color);
}
.ce-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  border-radius: 8px;
  background: rgba(0,0,0,.03);
  gap: 6px;
}
.ce-item-info {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  overflow: hidden;
  flex-wrap: wrap;
  font-size: 12px;
}
.cliche-collapse :deep(.n-collapse-item__header) {
  font-size: 13px;
}

.ce-card-lead {
  font-size: 12px;
  line-height: 1.55;
}

.ce-card-header-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.ce-card-header-title {
  font-size: 14px;
  font-weight: 600;
}

.ce-card-header-sub {
  font-size: 11px;
  line-height: 1.45;
}

.ce-group-label {
  font-size: 12px;
  letter-spacing: 0.02em;
}

.ce-id {
  font-size: 12px;
  font-weight: 500;
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.ce-id--inline {
  flex: 1;
}

.ce-notes {
  font-size: 11px;
  flex-basis: 100%;
  margin-top: 4px;
}

.ce-notes--inline {
  flex-basis: auto;
  margin-top: 0;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ce-beat-list {
  margin: 8px 0 0;
  padding-left: 1.2em;
  font-size: 12px;
  line-height: 1.55;
}

.ce-card-beats .ce-card-lead,
.ce-card-summary .ce-card-lead {
  margin-bottom: 8px;
}

.ce-k-hint {
  display: block;
  margin-top: 10px;
  font-size: 11px;
  line-height: 1.45;
}

.ce-inline-code {
  font-size: 11px;
  padding: 1px 4px;
  border-radius: 4px;
  background: var(--n-code-color);
}
</style>
