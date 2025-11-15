<template>
  <div class="auth-form-container">
    <form class="auth-form" @submit.prevent="submitUpdate">
      <h1 class="form-title">Edit Room</h1>
      
      <!-- General errors display -->
      <div v-show="generalErrors.length > 0" class="error-message">
        <font-awesome-icon icon="exclamation-circle" />
        <div class="error-list">
          <p v-for="(errMsg, index) in generalErrors" :key="index">{{ errMsg }}</p>
        </div>
      </div>

      <!-- Updated to support multiple topics with tag/chip interface -->
      <div class="form-group">
        <label for="topic-name">Topics (select one or more)</label>
        
        <!-- Selected topics display -->
        <div v-if="roomForm.topicNames && roomForm.topicNames.length > 0" class="selected-topics">
          <span 
            v-for="topicName in roomForm.topicNames" 
            :key="topicName"
            class="topic-tag"
          >
            {{ topicName }}
            <button 
              type="button" 
              class="remove-topic-btn"
              :title="`Remove ${topicName}`"
              @click="removeTopic(topicName)"
            >
              <font-awesome-icon icon="times" />
            </button>
          </span>
        </div>
        
        <div class="autocomplete-wrapper">
          <input
            id="topic-name"
            v-model="topicSearchInput"
            type="text"
            placeholder="Search or create topics"
            autocomplete="off"
            maxlength="32"
            :disabled="loading"
            :class="{ 'input-error': fieldErrors.topicNames }"
            @input="onTopicInput"
            @keydown.down.prevent="onArrowDown"
            @keydown.up.prevent="onArrowUp"
            @keydown.enter="onEnter"
            @blur="hideSuggestions"
            @keydown.esc="showSuggestions = false"
          />
          <div v-show="showSuggestions" class="suggestions-list">
            <div
              v-for="(topic, index) in filteredTopics"
              :key="topic"
              :class="['suggestion-item', { 
                active: index === selectedTopicIndex,
                selected: roomForm.topicNames?.includes(topic)
              }]"
              @mousedown="selectTopic(topic)"
              @mouseenter="selectedTopicIndex = index"
            >
              <span>{{ topic }}</span>
              <span v-if="roomForm.topicNames?.includes(topic)" class="selected-indicator">
                <font-awesome-icon icon="check" />
              </span>
            </div>
            <div v-if="filteredTopics.length === 0" class="no-suggestions">
              No matching topics found. Press Enter to create "{{ topicSearchInput }}"
            </div>
          </div>
        </div>
        <div class="char-count">
          {{ topicSearchInput.length }}/32
        </div>
        <div v-if="fieldErrors.topicNames" class="field-error">
          <p v-for="(errMsg, index) in fieldErrors.topicNames" :key="index">{{ errMsg }}</p>
        </div>
      </div>

      <div class="form-group">
        <label for="description">Description <span>(optional)</span></label>
        <textarea
          id="description"
          v-model="roomForm.description"
          placeholder="Add a description"
          maxlength="512"
          rows="4"
          :disabled="loading"
          :class="{ 'input-error': fieldErrors.description }"
        ></textarea>
        <div class="char-count">
          {{ roomForm.description!.length }}/512
        </div>
        <div v-if="fieldErrors.description" class="field-error">
          <p v-for="(errMsg, index) in fieldErrors.description" :key="index">{{ errMsg }}</p>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" :disabled="loading" @click="$emit('cancel')">
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="loading || !roomForm.topicNames || roomForm.topicNames.length === 0">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Updating...' : 'Update Room' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useUpdateRoom, useTopicsQuery } from "@/composables/useRooms";
import { parseGraphQLError } from '@/utils/errorParser';

import type { Topic, UpdateRoomInput } from '@/types';

const props = defineProps({
  room: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['cancel', 'updated']);

const { updateRoom, loading, error } = useUpdateRoom();
const { topics } = useTopicsQuery();

const roomForm = ref<UpdateRoomInput>({
  roomId: '',
  topicNames: [],
  description: ''
});

const topicSearchInput = ref<string>('');
const showSuggestions = ref<boolean>(false);
const selectedTopicIndex = ref<number>(-1);

watch(() => props.room, (newRoom) => {
  if (newRoom) {
    roomForm.value.roomId = newRoom.id;
    roomForm.value.topicNames = newRoom.topics?.map((t: Topic) => t.name) || [];
    roomForm.value.description = newRoom.description || '';
  }
}, { immediate: true });

onMounted(async () => {
  // Topics are automatically fetched by useTopicsQuery
});

const parsedErrors = computed(() => {
  if (!error.value) {
    return { fieldErrors: {}, generalErrors: [] }
  }
  return parseGraphQLError(error.value)
});

const fieldErrors = computed(() => parsedErrors.value.fieldErrors);
const generalErrors = computed(() => parsedErrors.value.generalErrors);

const filteredTopics = computed(() => {
  if (!topicSearchInput.value) return [];
  const searchTerm = topicSearchInput.value.toLowerCase();
  return topics.value
    .map((topic: Topic) => topic.name)
    .filter((topicName: string) => 
      topicName.toLowerCase().includes(searchTerm)
    );
});

// watch(roomForm, () => {
//   if (error.value) {
//     error.value = null;
//   }
// }, { deep: true });

function scrollToSelectedTopic() {
  if (selectedTopicIndex.value >= 0) {
    const suggestionsList = document.querySelector('.suggestions-list');
    const selectedItem = suggestionsList?.children[selectedTopicIndex.value];
    
    if (suggestionsList && selectedItem) {
      const listRect = suggestionsList.getBoundingClientRect();
      const itemRect = selectedItem.getBoundingClientRect();
      
      if (itemRect.bottom > listRect.bottom) {
        suggestionsList.scrollTop += itemRect.bottom - listRect.bottom + 5;
      } else if (itemRect.top < listRect.top) {
        suggestionsList.scrollTop -= listRect.top - itemRect.top + 5;
      }
    }
  }
}

function onTopicInput() {
  showSuggestions.value = true;
  selectedTopicIndex.value = -1;
}

function onArrowDown() {
  if (selectedTopicIndex.value < filteredTopics.value.length - 1) {
    selectedTopicIndex.value++;
    scrollToSelectedTopic();
  }
}

function onArrowUp() {
  if (selectedTopicIndex.value > -1) {
    selectedTopicIndex.value--;
    scrollToSelectedTopic();
  }
}

function onEnter(event: KeyboardEvent) {
  if (!showSuggestions.value && !topicSearchInput.value.trim()) {
    return;
  }

  event.preventDefault();

  if (selectedTopicIndex.value >= 0 && filteredTopics.value[selectedTopicIndex.value]) {
    selectTopic(filteredTopics.value[selectedTopicIndex.value]);
  } else if (filteredTopics.value.length === 1 && filteredTopics.value[0]) {
    selectTopic(filteredTopics.value[0]);
  } else if (topicSearchInput.value.trim()) {
    // Create new topic if no match found
    selectTopic(topicSearchInput.value.trim());
  }

  showSuggestions.value = false;
}

function selectTopic(topic: string) {
  if (!roomForm.value.topicNames) {
    roomForm.value.topicNames = [];
  }
  if (!roomForm.value.topicNames.includes(topic)) {
    roomForm.value.topicNames.push(topic);
  }
  topicSearchInput.value = '';
  showSuggestions.value = false;
  selectedTopicIndex.value = -1;
}

function removeTopic(topicName: string) {
  if (roomForm.value.topicNames) {
    roomForm.value.topicNames = roomForm.value.topicNames.filter(t => t !== topicName);
  }
}

function hideSuggestions() {
  setTimeout(() => {
    showSuggestions.value = false;
    selectedTopicIndex.value = -1;
  }, 150);
}

async function submitUpdate() {
  if (!roomForm.value.topicNames || roomForm.value.topicNames.length === 0) return;

  const result = await updateRoom({ ...roomForm.value });
  
  if (result.success) {
    emit('updated', result.room);
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';
@import '@/assets/styles/form-errors.css';

/* Show the form title and style it properly */
.form-title {
  margin-bottom: 1rem;
  text-align: center;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 600;
}

/* Match CreateRoom styling for selected topics */
.selected-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background-color: var(--bg-color);
  border-radius: var(--radius);
  min-height: 40px;
}

.topic-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background-color: var(--primary-color);
  color: white !important;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.remove-topic-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition);
  font-size: 0.75rem;
}

.remove-topic-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.autocomplete-wrapper {
  position: relative;
}

.suggestions-list {
  position: absolute;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  background: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  z-index: 100;
  margin-top: 0.25rem;
  scroll-behavior: smooth;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: var(--transition);
}

.suggestion-item:hover,
.suggestion-item.active {
  background-color: var(--bg-color);
}

/* Style for already selected topics in dropdown */
.suggestion-item.selected {
  background-color: rgba(79, 70, 229, 0.1);
  color: var(--primary-color);
}

.selected-indicator {
  color: var(--primary-color);
  font-size: 0.8rem;
}

.no-suggestions {
  padding: 0.75rem 1rem;
  color: var(--text-light);
  font-size: 0.875rem;
}

.form-group textarea {
  width: 100%;
  box-sizing: border-box;
  min-height: 100px;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: var(--white);
  transition: var(--transition);
  resize: none;
}

.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-group span {
  color: var(--text-light);
  font-size: 0.875rem;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.8rem;
  color: var(--text-light);
  margin-top: 0.25rem;
  flex-shrink: 0;
}

/* Update form actions to match CreateRoom button styling but keep both buttons */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--white);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--bg-color);
}

.spinner {
  border: 2px solid rgba(255, 255, 255, 0.3);
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border-left-color: var(--white);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Ensure the form container matches CreateRoom styling */
.auth-form-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Reduce the vertical gap between form elements */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
