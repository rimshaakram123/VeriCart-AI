<template>
  <div class="tb-card" :class="{ 'tb-card--static': !clickable }" @click="clickable ? goDetail() : null">
    <div class="img-wrapper" v-if="showImage">
      <img v-if="!imgFailed && imageUrl" :src="imageUrl" :alt="product.name" loading="lazy" @error="imgFailed = true" />
      <div v-else class="img-fallback">
        <el-icon class="fallback-icon"><component :is="categoryIcon" /></el-icon>
      </div>

      <!-- Trust score chip -->
      <span v-if="product.trustScore" :class="['img-trust', trustLevelClass]" :title="`AI Trust Score ${product.trustScore}/100`">
        <el-icon><CircleCheck /></el-icon> {{ product.trustScore }}
      </span>

      <!-- Discount badge -->
      <span class="discount-badge" v-if="product.originalPrice && product.originalPrice > product.price">
        -{{ discountPercent }}%
      </span>
    </div>

    <div class="info">
      <div class="title">{{ product.name.replace(/^SEED:/, '') }}</div>
      <div class="price-row">
        <span class="price"><span class="symbol">¥</span>{{ formatPrice(product.price) }}</span>
        <span class="original-price" v-if="product.originalPrice && product.originalPrice > product.price">
          ¥{{ formatPrice(product.originalPrice) }}
        </span>
      </div>
      <div class="meta">
        <StarRating :rating="product.rating" :size="12" />
        <span class="reviews">{{ product.reviewCount || 0 }} reviews</span>
        <span v-if="product.brand" class="brand">{{ product.brand }}</span>
      </div>
      <div class="variants" v-if="variantGroups.length">
        <div class="v-group" v-for="g in variantGroups.slice(0, 2)" :key="g.name">
          <span class="v-name">{{ g.name }}</span>
          <button
            v-for="opt in g.options.slice(0, 3)"
            :key="opt"
            type="button"
            :class="['v-chip', { active: selectedVariants[g.name] === opt }]"
            @click.stop="selectVariant(g.name, opt)"
          >{{ opt }}</button>
          <span v-if="g.options.length > 3" class="v-more">+{{ g.options.length - 3 }}</span>
        </div>
      </div>
      <slot name="actions" />

      <button class="details-toggle" @click.stop="toggleDetails" type="button">
        <el-icon><Document /></el-icon>
        <span>Product Details / Reviews ({{ product.reviewCount || 0 }})</span>
        <el-icon class="chev" :class="{ open: expanded }"><ArrowDown /></el-icon>
      </button>

      <div v-if="expanded" class="details-panel">
        <section v-if="product.description">
          <h4>Description</h4>
          <p>{{ product.description }}</p>
        </section>

        <section v-if="aiSummaryText">
          <h4>AI Review Summary</h4>
          <p class="ai-summary">{{ aiSummaryText }}</p>
        </section>

        <section class="trust-row">
          <h4>Trust Score</h4>
          <span v-if="product.trustScore" :class="['trust-pill', trustLevelClass]">
            Score {{ product.trustScore }}/100 · {{ product.trustLevel }}
          </span>
          <span v-if="product.fakeReviewCount" class="fake">Suspected fake: {{ product.fakeReviewCount }}</span>
          <span v-if="product.stock != null" class="stock">Stock: {{ product.stock }}</span>
        </section>

        <section class="reviews-sec">
          <h4>Customer Reviews</h4>
          <div v-if="loadingReviews" class="loading">Loading…</div>
          <div v-else-if="reviews.length === 0" class="empty">No reviews yet</div>
          <template v-else>
            <div v-for="rv in reviews.slice(0, 3)" :key="rv.id" class="review-item">
              <div class="rv-head">
                <span class="rv-user">{{ rv.username || 'Anonymous' }}</span>
                <StarRating :rating="rv.rating" :size="11" />
                <span v-if="rv.verified" class="rv-verified">Verified</span>
              </div>
              <p class="rv-content">{{ rv.content }}</p>
            </div>
            <button class="view-all" @click.stop="clickable ? goDetail() : null">View all {{ product.reviewCount || 0 }} reviews →</button>
          </template>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  Monitor, ShoppingBag, House, Reading, Football, Refrigerator,
  MagicStick, Present, Van, Brush, Apple, Goods,
  CircleCheck, Document, ArrowDown
} from '@element-plus/icons-vue'
import StarRating from './StarRating.vue'
import { reviewApi } from '@/api'
import { parseVariants, defaultSelection } from '@/utils/variants'

const props = defineProps({
  product: { type: Object, required: true },
  showImage: { type: Boolean, default: true },
  clickable: { type: Boolean, default: true }
})

const router = useRouter()
const imgFailed = ref(false)

const CATEGORY_ICONS = {
  1: Monitor, 2: ShoppingBag, 3: House, 4: Reading, 5: Football,
  26: MagicStick, 30: Present, 34: Apple, 42: Refrigerator, 46: Van, 50: Brush
}
const imageUrl = computed(() => {

  let images = props.product.images

  if (!images || images === "[]") {
    return ''
  }

  try {
    if (typeof images === 'string') {
      images = JSON.parse(images)
    }

    if (Array.isArray(images) && images.length > 0) {
      return images[0]
    }

  } catch (e) {
    console.log("Image parse error:", e)
  }

  return ''

})

const discountPercent = computed(() => {
  if (!props.product?.originalPrice || !props.product?.price) return 0
  return Math.round((1 - props.product.price / props.product.originalPrice) * 100)
})

const categoryIcon = computed(() => CATEGORY_ICONS[props.product?.categoryId] || Goods)

const variantGroups = computed(() => parseVariants(props.product))
const selectedVariants = reactive(defaultSelection(variantGroups.value))
function selectVariant(name, opt) { selectedVariants[name] = opt }

// ---- Expandable details + reviews panel ----
const expanded = ref(false)
const reviews = ref([])
const loadingReviews = ref(false)
const reviewsLoaded = ref(false)

const aiSummaryText = computed(() => {
  const t = props.product?.aiSummary
  if (!t) return ''
  return t
    .replace(/^#+\s*/gm, '')
    .replace(/\*\*/g, '')
    .replace(/\n{2,}/g, '\n')
    .trim()
})

async function loadReviews() {
  if (reviewsLoaded.value) return
  loadingReviews.value = true
  try {
    const res = await reviewApi.byProduct(props.product.id)
    reviews.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    reviews.value = []
  } finally {
    loadingReviews.value = false
    reviewsLoaded.value = true
  }
}

function toggleDetails() {
  expanded.value = !expanded.value
  if (expanded.value) loadReviews()
}

const trustLevelClass = computed(() => {
  const s = props.product?.trustScore
  if (!s) return ''
  if (s >= 85) return 'trust-excellent'
  if (s >= 70) return 'trust-high'
  if (s >= 50) return 'trust-medium'
  return 'trust-low'
})

function formatPrice(v) {
  const n = Number(v || 0)
  return Number.isInteger(n) ? String(n) : n.toFixed(2)
}

function goDetail() {
  router.push(`/products/${props.product.id}`)
}
</script>

<style scoped>
.tb-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow .2s ease, transform .2s ease;
}
.tb-card:hover {
  box-shadow: 0 8px 24px rgba(255, 68, 0, .18);
  transform: translateY(-2px);
}
.tb-card--static {
  cursor: default;
}
.tb-card--static:hover {
  box-shadow: none;
  transform: none;
}

.img-wrapper {
  position: relative;
  aspect-ratio: 1 / 1;
  background: #fafafa;
  overflow: hidden;
}
.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.img-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FFEFEC 0%, #FFE2DD 100%);
  color: var(--primary);
}
.fallback-icon { font-size: 44px; }

.img-trust {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  background: rgba(255, 255, 255, .94);
  backdrop-filter: blur(6px);
  box-shadow: 0 1px 4px rgba(0, 0, 0, .12);
}
.img-trust .el-icon { font-size: 12px; }
.trust-excellent { color: #2ba471; }
.trust-high { color: #ff7a00; }
.trust-medium { color: #b88230; }
.trust-low { color: #c0392b; }

.discount-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #ff4400, #ff7300);
}

.info {
  padding: 10px 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.title {
  font-size: 13px;
  line-height: 1.4;
  color: #333;
  height: 36px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.price {
  color: #ff4400;
  font-size: 18px;
  font-weight: 800;
}
.price .symbol {
  font-size: 13px;
  margin-right: 1px;
}
.original-price {
  color: #999;
  font-size: 12px;
  text-decoration: line-through;
}
.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
}
.meta .reviews { color: #888; }
.meta .brand {
  margin-left: auto;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #bbb;
  font-weight: 600;
}
.variants {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.v-group {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.v-name {
  font-size: 11px;
  color: #999;
  margin-right: 2px;
}
.v-chip {
  border: 1px solid #e3e3e3;
  background: #fff;
  color: #555;
  border-radius: 4px;
  padding: 2px 7px;
  font-size: 11px;
  cursor: pointer;
  transition: all .15s ease;
}
.v-chip:hover { border-color: #ff4400; color: #ff4400; }
.v-chip.active {
  border-color: #ff4400;
  color: #ff4400;
  background: #fff3ee;
  font-weight: 700;
}
.v-more { font-size: 11px; color: #bbb; }

/* Expandable details + reviews panel */
.details-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  margin-top: 4px;
  padding: 7px 10px;
  border: 1px solid #ffe0d6;
  background: #fff7f4;
  color: #ff4400;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.details-toggle:hover { background: #ffefe9; }
.details-toggle .chev { margin-left: auto; transition: transform .2s ease; }
.details-toggle .chev.open { transform: rotate(180deg); }

.details-panel {
  margin-top: 8px;
  border-top: 1px dashed #eee;
  padding-top: 10px;
  font-size: 12px;
  color: #444;
}
.details-panel h4 {
  margin: 10px 0 5px;
  font-size: 12px;
  color: #222;
  font-weight: 700;
}
.details-panel h4:first-child { margin-top: 0; }
.details-panel p { margin: 0; line-height: 1.5; color: #555; }
.ai-summary {
  background: #f8fafc;
  border-radius: 6px;
  padding: 8px 10px;
  white-space: pre-wrap;
  max-height: 130px;
  overflow: auto;
}
.trust-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.trust-pill {
  padding: 2px 8px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 11px;
  background: #f3f4f6;
  color: #555;
}
.trust-pill.trust-excellent { background: #e7f7ef; color: #2ba471; }
.trust-pill.trust-high { background: #fff1e6; color: #ff7a00; }
.trust-pill.trust-medium { background: #fdf6e7; color: #b88230; }
.trust-pill.trust-low { background: #fdecea; color: #c0392b; }
.fake, .stock { font-size: 11px; color: #888; }
.reviews-sec { margin-top: 4px; }
.reviews-sec .loading, .reviews-sec .empty { color: #aaa; padding: 6px 0; }
.review-item { border-top: 1px solid #f3f3f3; padding: 7px 0; }
.rv-head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}
.rv-user { font-weight: 700; color: #333; font-size: 12px; }
.rv-verified {
  font-size: 10px;
  color: #2ba471;
  border: 1px solid #2ba471;
  border-radius: 4px;
  padding: 0 4px;
}
.rv-content { margin: 0; color: #555; line-height: 1.5; }
.view-all {
  margin-top: 8px;
  background: none;
  border: none;
  color: #ff4400;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
}
</style>
