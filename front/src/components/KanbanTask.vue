<template>
  <div
    class="kanban-task"
    draggable="true"
    @dragstart="$emit('dragstart', $event, task)"
    @dblclick="$emit('edit', task)"
  >
    <div class="task-header">
      <h4>{{ task.title }}</h4>
      <span class="task-priority" :class="priorityClass">{{ task.priority }}</span>
    </div>
    <div class="task-users">
      👤 {{ task.users.map(u => u.name).join(", ") }}
    </div>
    <p class="task-description">{{ task.description }}</p>
    <div class="task-footer">
      <span v-if="task.due_date" class="task-due-date">
        📅 {{ formatDate(task.due_date) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  task: { type: Object, required: true }
});
const emit = defineEmits(['dragstart']);

// Priority class
const priorityClass = computed(() => {
  return {
    'priority-low': props.task.priority === 'basse',
    'priority-medium': props.task.priority === 'moyenne',
    'priority-high': props.task.priority === 'haute',
    'priority-critical': props.task.priority === 'critique'
  };
});

// Format date
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR');
};

const onDragStart = (event) => {
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', String(props.task.id));
  emit('dragstart', String(props.task.id));
};
</script>

<style scoped>
.kanban-task {
  background-color: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: grab;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kanban-task:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.kanban-task:active {
  cursor: grabbing;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #2f4f4f;
}

.task-description {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #495057;
  white-space: pre-line;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6c757d;
}

.task-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.priority-low {
  background-color: #d4edda;
  color: #155724;
}

.priority-medium {
  background-color: #fff3cd;
  color: #856404;
}

.priority-high {
  background-color: #ffeeba;
  color: #856404;
}

.priority-critical {
  background-color: #f8d7da;
  color: #721c24;
}

.task-due-date {
  font-size: 12px;
}

.add-task {
  background-color: #e9ecef;
  border-radius: 6px;
  padding: 10px;
  text-align: center;
  color: #6c757d;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.add-task:hover {
  background-color: #dee2e6;
}
</style>
