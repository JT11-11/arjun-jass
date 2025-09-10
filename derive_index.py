from helper.data import atomic_congestion_indexer, cost_sharing_indexer, dictator_indexer, social_context_indexer
from helper.data import prisonner_dilemma
from helper.data.non_atomic_indexer import NonAtomicIndexer
from helper.data.prisonner_dilemma import PrisonersDilemmaIndexer
from helper.data.social_context_indexer import SocialContextIndexer

# ----------------------------
# Non-Atomic Congestion Indexer
# ----------------------------
print("=== Non-Atomic Congestion Indexer ===")
non_atomic_indexer = NonAtomicIndexer(csv_file="data/non_atomic_results.csv")
print(f"LLMs indexed: {non_atomic_indexer.all_indices()}")
print("Altruism per LLM:")
for llm, value in non_atomic_indexer.altruism.items():
    print(f"  {llm}: {value}")
print()

# ----------------------------
# Social Context Indexer
# ----------------------------
print("=== Social Context Indexer ===")
social_context_indexer = SocialContextIndexer("data/social_context_results.csv")
print(f"LLMs indexed: {social_context_indexer.all_indices()}")
print("Altruism per LLM:")
for llm, value in social_context_indexer.altruism.items():
    print(f"  {llm}: {value}")
print()

# ----------------------------
# Dictator Game Indexer
# ----------------------------
print("=== Dictator Game Indexer ===")
dictator_indexer_obj = dictator_indexer.DictatorGameIndexer("data/dictator_game_results.csv")
print(f"LLMs indexed: {dictator_indexer_obj.all_indices()}")
print("Altruism per LLM:")
for llm, value in dictator_indexer_obj.altruism.items():
    print(f"  {llm}: {value}")
print("Utility per LLM:")
for llm, value in dictator_indexer_obj.utility.items():
    print(f"  {llm}: {value}")
print()

# ----------------------------
# Atomic Congestion Indexer
# ----------------------------
print("=== Atomic Congestion Indexer ===")
atomic_congestion_indexer_obj = atomic_congestion_indexer.AtomicCongestionIndexer("data/atomic_congestion_all.csv")
print(f"LLMs indexed: {atomic_congestion_indexer_obj.all_indices()}")
print("Altruism per LLM:")
for llm, measures in atomic_congestion_indexer_obj.altruism.items():
    print(f"  {llm}: {measures}")
print()

# ----------------------------
# Cost Sharing Scheduler Indexer
# ----------------------------
print("=== Cost Sharing Scheduler Indexer ===")
cost_sharing_indexer_obj = cost_sharing_indexer.CostSharingSchedulerIndexer("data/cost_sharing_game_results.csv")
print(f"LLMs indexed: {cost_sharing_indexer_obj.all_indices()}")
print("Altruism per LLM:")
for llm, value in cost_sharing_indexer_obj.altruism.items():
    print(f"  {llm}: {value}")
print("Utility per LLM:")
for llm, value in cost_sharing_indexer_obj.utility.items():
    print(f"  {llm}: {value}")
print()

# ----------------------------
# Prisoner's Dilemma Indexer
# ----------------------------
print("=== Prisoner's Dilemma Indexer ===")
prisonner_dilemma_indexer_obj = PrisonersDilemmaIndexer("data/prisoner_dilemma.csv")
print(f"LLMs indexed: {prisonner_dilemma_indexer_obj.all_indices()}")
print("Altruism per LLM:")
for llm, measures in prisonner_dilemma_indexer_obj.altruism.items():
    print(f"  {llm}: {measures}")
print()
