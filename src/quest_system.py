import json
from enum import Enum

class QuestState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"  # Награда получена

class Quest:
    def __init__(self, quest_id, name, description, target_item, target_count, reward_text, giver_npc):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.target_item = target_item
        self.target_count = target_count
        self.reward_text = reward_text
        self.giver_npc = giver_npc  # Кто выдал квест
        self.state = QuestState.NOT_STARTED
        self.collected = 0
        
    def start(self):
        if self.state == QuestState.NOT_STARTED:
            self.state = QuestState.IN_PROGRESS
            return True
        return False
    
    def add_item(self, item_name):
        if self.state == QuestState.IN_PROGRESS and item_name == self.target_item:
            self.collected += 1
            if self.collected >= self.target_count:
                self.state = QuestState.COMPLETED
            return True
        return False
    
    def claim_reward(self):
        if self.state == QuestState.COMPLETED:
            self.state = QuestState.CLAIMED
            return self.reward_text
        return None
    
    def get_progress_text(self):
        return f"{self.collected}/{self.target_count}"

class QuestSystem:
    def __init__(self, quest_file="data/quests.json"):
        self.quests = {}
        self.active_quest = None
        self.load_quests(quest_file)
    
    def load_quests(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for qid, qdata in data.items():
                    self.quests[qid] = Quest(
                        quest_id=qid,
                        name=qdata['name'],
                        description=qdata['description'],
                        target_item=qdata['target_item'],
                        target_count=qdata['target_count'],
                        reward_text=qdata['reward_text'],
                        giver_npc=qdata['giver_npc']
                    )
        except FileNotFoundError:
            print(f"Файл {filepath} не найден, создаю квесты по умолчанию")
            self._create_default_quests()
    
    def _create_default_quests(self):
        """Создаёт 3 квеста от Сасаныча"""
        self.quests["quest_herbs"] = Quest(
            quest_id="quest_herbs",
            name="Травы для Мишани",
            description="Собери 3 целебные травы для Садовода Мишани в лесу.",
            target_item="Трава",
            target_count=3,
            reward_text="Мишаня доволен! Возвращайся к Сасанычу.",
            giver_npc="NPC_1"  # Сасаныч
        )
        self.quests["quest_potion"] = Quest(
            quest_id="quest_potion",
            name="Зелье для Додошки",
            description="Отнеси целебное зелье Старичку Додошке на озеро.",
            target_item="Зелье",
            target_count=1,
            reward_text="Додошка благодарит тебя! Возвращайся к Сасанычу.",
            giver_npc="NPC_1"
        )
        self.quests["quest_map"] = Quest(
            quest_id="quest_map",
            name="Потерянная карта",
            description="Найди карту, которую Сасаныч потерял в лесу.",
            target_item="Карта",
            target_count=1,
            reward_text="Сасаныч очень рад! Теперь он может дать тебе награду.",
            giver_npc="NPC_1"
        )
    
    def start_quest(self, quest_id):
        if quest_id in self.quests:
            return self.quests[quest_id].start()
        return False
    
    def on_item_picked(self, item_name):
        """Вызывается при подборе предмета — обновляет прогресс квестов"""
        updated_quests = []
        for quest in self.quests.values():
            if quest.add_item(item_name):
                updated_quests.append(quest)
        return updated_quests
    
    def get_quest_by_giver(self, npc_id):
        """Возвращает квесты от конкретного NPC"""
        return [q for q in self.quests.values() if q.giver_npc == npc_id]
    
    def get_active_quests(self):
        """Возвращает активные квесты"""
        return [q for q in self.quests.values() if q.state == QuestState.IN_PROGRESS]
    
    def get_completed_quests(self):
        """Возвращает завершённые квесты (ожидают награды)"""
        return [q for q in self.quests.values() if q.state == QuestState.COMPLETED]
    
    def get_claimed_quests(self):
        """Возвращает выполненные квесты (награда получена)"""
        return [q for q in self.quests.values() if q.state == QuestState.CLAIMED]
    
    def all_quests_completed(self):
        """Проверяет, все ли 3 квеста выполнены"""
        completed = self.get_completed_quests()
        return len(completed) >= 3
    
    def get_quest_state(self, quest_id):
        if quest_id in self.quests:
            return self.quests[quest_id].state
        return None