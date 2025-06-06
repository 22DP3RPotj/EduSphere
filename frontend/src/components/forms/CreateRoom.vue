<template>
  <div class="auth-form-container">
    <form class="auth-form" @submit.prevent="submitRoom">
      <h2 class="form-title">Create Room</h2>
      
      <div class="form-group">
        <label for="room-name">Room Name</label>
        <input
          id="room-name"
          v-model="roomForm.name"
          type="text"
          placeholder="Enter room name"
          autocomplete="off"
          required
        >
      </div>

      <div class="form-group">
        <label for="topic-name">Topic</label>
        <div class="autocomplete-wrapper">
          <input
            id="topic-name"
            v-model="roomForm.topicName"
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
          v-model="roomForm.description"
          placeholder="Add a description"
          maxlength="500"
          rows="4"
        ></textarea>
        <div class="char-count">
          {{ roomForm.description.length }}/500
        </div>
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        <span v-if="isLoading" class="spinner"></span>
        {{ isLoading ? 'Creating...' : 'Create Room' }}
      </button>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useRoomApi } from "@/api/room.api";

import type { Topic, CreateRoomInput } from '@/types';

const router = useRouter();
const { createRoom, fetchTopics } = useRoomApi();

const roomForm = ref<CreateRoomInput>({
  name: '',
  topicName: '',
  description: ''
});
const isLoading = ref<boolean>(false);
const topics = ref<Topic[]>([]);
const showSuggestions = ref<boolean>(false);
const selectedTopicIndex = ref<number>(-1);

onMounted(async () => {
  try {
    const topicsResponse = await fetchTopics();
    topics.value = [...topicsResponse];
  } catch (error) {
    console.error('Error fetching topics:', error);
  }
});

const filteredTopics = computed(() => {
  if (!roomForm.value.topicName) return [];
  const searchTerm = roomForm.value.topicName.toString().toLowerCase();
  return topics.value.map(({ name }) => name).filter(topic => 
    topic.toLowerCase().includes(searchTerm)
  );
});

function scrollToSelectedTopic() {
  if (selectedTopicIndex.value >= 0) {
    const suggestionsList = document.querySelector('.suggestions-list');
    const selectedItem = suggestionsList?.children[selectedTopicIndex.value];
    
    if (suggestionsList && selectedItem) {
      const listRect = suggestionsList.getBoundingClientRect();
      const itemRect = selectedItem.getBoundingClientRect();
      
      if (itemRect.bottom > listRect.bottom) {
        suggestionsList.scrollTop += itemRect.bottom - listRect.bottom + 5;
      }

      else if (itemRect.top < listRect.top) {
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
  roomForm.value.topicName = topic;
  showSuggestions.value = false;
}

async function submitRoom() {
  if (!roomForm.value.name || !roomForm.value.topicName) return;

  isLoading.value = true;
  try {
    const room = await createRoom({ ...roomForm.value });

    if (room) {
      router.push(`/u/${room.host.username}/${room.slug}`);
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';

.autocomplete-wrapper {
  position: relative;
}

.suggestions-list {
  position: absolute;
  width: 90%;
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
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: var(--transition);
}

.suggestion-item:hover,
.suggestion-item.active {
  background-color: var(--bg-color);
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
</style>