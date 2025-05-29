<template>
  <div class="auth-form-container">
    <form @submit.prevent="submitRoom" class="auth-form">
      <h2 class="form-title">Create Room</h2>
      
      <div class="form-group">
        <label for="room-name">Room Name</label>
        <input
          id="room-name"
          v-model="name"
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
              @click="selectTopic(topic)"
              :class="['suggestion-item', { active: index === selectedTopicIndex }]"
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

      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        <span v-if="isLoading" class="spinner"></span>
        {{ isLoading ? 'Creating...' : 'Create Room' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoomApi } from "@/api/room.api";

const { createRoom, fetchTopics } = useRoomApi();

const name = ref('');
const topicInput = ref('');
const description = ref('');
const isLoading = ref(false);
const topics = ref([]);
const showSuggestions = ref(false);
const selectedTopicIndex = ref(-1);

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

function onEnter(event) {
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

function selectTopic(topic) {
  topicInput.value = topic;
  showSuggestions.value = false;
}

async function submitRoom() {
  if (!name.value || !topicInput.value) return;

  isLoading.value = true;
  try {
    await createRoom(
      name.value, 
      topicInput.value, 
      description.value || null
    );
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
  width: 90%;
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
</style>