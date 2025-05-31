<template>
  <div class="auth-form-container">
    <form class="auth-form" @submit.prevent="submitUpdate">
      <h2 class="form-title">Edit Room</h2>
      
      <div class="form-group">
        <label for="topic-name">Topic</label>
        <div class="autocomplete-wrapper">
          <input
            id="topic-name"
            v-model="topicInput"
            type="text"
            placeholder="Search or create topic"
            autocomplete="off"
            required
            @input="onTopicInput"
            @keydown.down.prevent="onArrowDown"
            @keydown.up.prevent="onArrowUp"
            @keydown.enter="onEnter"
            @blur="showSuggestions = false"
            @keydown.esc="showSuggestions = false"
          />
          <div v-show="showSuggestions" class="suggestions-list">
            <div
              v-for="(topic, index) in filteredTopics"
              :key="topic"
              :class="['suggestion-item', { active: index === selectedTopicIndex }]"
              @click="selectTopic(topic)"
            >
              {{ topic }}
            </div>
            <div v-if="filteredTopics.length === 0" class="no-suggestions">
              No matching topics found. You might want to create a new one.
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="description">Description <span>(optional)</span></label>
        <textarea
          id="description"
          v-model="description"
          placeholder="Add a description"
          rows="4"
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          {{ isLoading ? 'Updating...' : 'Update Room' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoomApi } from "@/api/room.api";

import type { Topic } from '@/types';

const props = defineProps({
  room: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['cancel', 'updated']);

const { updateRoom, fetchTopics } = useRoomApi();

const topicInput = ref<string>('');
const description = ref<string | undefined>(undefined);
const isLoading = ref<boolean>(false);
const topics = ref<Topic[]>([]);
const showSuggestions = ref<boolean>(false);
const selectedTopicIndex = ref<number>(-1);


watch(() => props.room, (newRoom) => {
  if (newRoom) {
    topicInput.value = newRoom.topic?.name || '';
    description.value = newRoom.description || undefined;
  }
}, { immediate: true });

onMounted(async () => {
  try {
    const topicsResponse = await fetchTopics();
    topics.value = [...topicsResponse];
  } catch (error) {
    console.error('Error fetching topics:', error);
  }
});

const filteredTopics = computed(() => {
  if (!topicInput.value) return [];
  const searchTerm = topicInput.value.toString().toLowerCase();
  return topics.value.map(({ name }) => name).filter(topic => 
    topic.toLowerCase().includes(searchTerm)
  );
});

function onTopicInput() {
  showSuggestions.value = true;
  selectedTopicIndex.value = -1;
}

function onArrowDown() {
  if (selectedTopicIndex.value < filteredTopics.value.length - 1) {
    selectedTopicIndex.value++;
  }
}

function onArrowUp() {
  if (selectedTopicIndex.value > -1) {
    selectedTopicIndex.value--;
  }
}

function onEnter(event: KeyboardEvent) {
  if (!showSuggestions.value) {
    return;
  }

  event.preventDefault();

  if (selectedTopicIndex.value >= 0) {
    selectTopic(filteredTopics.value[selectedTopicIndex.value]);
  } else if (filteredTopics.value.length === 1) {
    selectTopic(filteredTopics.value[0]);
  }

  showSuggestions.value = false;
}

function selectTopic(topic: string) {
  topicInput.value = topic;
  showSuggestions.value = false;
}

async function submitUpdate() {
  if (!topicInput.value) return;

  isLoading.value = true;
  try {
    const updatedRoom = await updateRoom({
      hostSlug: props.room.host.username,
      roomSlug: props.room.slug,
      topicName: topicInput.value,
      description: description.value
    });
    
    if (updatedRoom) {
      emit('updated', updatedRoom);
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.auth-form-container {
  padding: 2rem;
}

.auth-form {
  background: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.form-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--text-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.form-group span {
  color: var(--text-light);
  font-size: 0.875rem;
}

.autocomplete-wrapper {
  position: relative;
}

input, textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 1rem;
  color: var(--text-color);
  background: var(--white);
  transition: var(--transition);
}

input:focus, textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

textarea {
  min-height: 100px;
  resize: none;
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
  margin-top: 0.5rem;
}

.suggestion-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: var(--transition);
  color: var(--text-color);
}

.suggestion-item:hover,
.suggestion-item.active {
  background-color: var(--bg-color);
  color: var(--primary-color);
}

.no-suggestions {
  padding: 0.75rem 1rem;
  color: var(--text-light);
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
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
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background-color: var(--border-color);
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

@media (max-width: 768px) {
  .auth-form-container {
    padding: 1rem;
  }
  
  .form-actions {
    flex-direction: column-reverse;
    gap: 0.75rem;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>