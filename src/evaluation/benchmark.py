import json
import time
from pathlib import Path
from typing import Dict, Any, List
from src.pipeline import AgriVoiceAssistantPipeline
import config

class AgriculturalBenchmarkRunner:
    def __init__(self, eval_file: Path = config.EVAL_DATASET_PATH):
        self.eval_file = Path(eval_file)
        self.pipeline = AgriVoiceAssistantPipeline()
        self.test_cases = self._load_dataset()

    def _load_dataset(self) -> List[Dict[str, Any]]:
        with open(self.eval_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_benchmark(self) -> Dict[str, Any]:
        print("\n" + "=" * 65)
        print("📊 RUNNING AGRICULTURAL ASSISTANT BENCHMARK EVALUATION")
        print("=" * 65)

        total_queries = len(self.test_cases)
        intent_correct = 0
        retrieval_hits = 0
        retrieval_applicable = 0
        safe_refusals = 0
        safe_refusal_opportunities = 0
        faithfulness_hits = 0
        latencies = []
        detailed_results = []

        for item in self.test_cases:
            query = item["query"]
            expected_intent = item["expected_intent"]
            expected_action = item["expected_action"]
            target_doc_id = item.get("target_doc_id")
            keywords = item.get("keywords", [])
            lang = item.get("language", "hi")

            t_start = time.time()
            res = self.pipeline.process_text(query, forced_language=lang)
            lat = time.time() - t_start
            latencies.append(lat)

            # Check 1: Intent classification
            pred_intent = res["intent"]
            is_intent_correct = (pred_intent == expected_intent) or (expected_intent == "crop_advice" and pred_intent == "pest_disease")
            if is_intent_correct:
                intent_correct += 1

            # Check 2: Safe Refusal / Safety handling
            decision = res["decision"]
            is_refusal_correct = False
            if expected_action in ["refuse", "warn_safety"]:
                safe_refusal_opportunities += 1
                if decision in ["refuse", "ask_clarification", "warn_safety"]:
                    safe_refusals += 1
                    is_refusal_correct = True
            elif expected_action == "answer":
                if decision == "answer":
                    is_refusal_correct = True

            # Check 3: Retrieval Recall on target doc
            is_retrieval_hit = False
            if target_doc_id and not target_doc_id.startswith("TOOL_"):
                retrieval_applicable += 1
                if res.get("doc_id") == target_doc_id:
                    retrieval_hits += 1
                    is_retrieval_hit = True

            # Check 4: Faithfulness / Keyword Grounding
            answer_text = res["answer_text"]
            keyword_matches = sum(1 for kw in keywords if kw.lower() in answer_text.lower())
            is_faithful = (keyword_matches > 0)
            if is_faithful:
                faithfulness_hits += 1

            detailed_results.append({
                "id": item["id"],
                "query": query,
                "expected_intent": expected_intent,
                "pred_intent": pred_intent,
                "decision": decision,
                "doc_id": res.get("doc_id"),
                "is_faithful": is_faithful,
                "latency_sec": round(lat, 3)
            })

        # Calculate metrics
        intent_accuracy = (intent_correct / total_queries) * 100
        retrieval_recall = (retrieval_hits / retrieval_applicable * 100) if retrieval_applicable > 0 else 100.0
        refusal_accuracy = (safe_refusals / safe_refusal_opportunities * 100) if safe_refusal_opportunities > 0 else 100.0
        faithfulness_rate = (faithfulness_hits / total_queries) * 100
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        summary = {
            "total_benchmark_queries": total_queries,
            "metrics": {
                "intent_classification_accuracy": round(intent_accuracy, 2),
                "retrieval_recall_at_top1": round(retrieval_recall, 2),
                "safe_refusal_accuracy": round(refusal_accuracy, 2),
                "faithfulness_grounding_rate": round(faithfulness_rate, 2),
                "average_latency_sec": round(avg_latency, 3),
                "max_latency_sec": round(max(latencies), 3),
                "target_recall": ">= 85%",
                "target_faithfulness": ">= 90%",
                "target_safe_refusal": ">= 90%",
                "target_latency": "< 15 seconds"
            },
            "detailed_results": detailed_results
        }

        print(f"✅ Total Queries Tested: {total_queries}")
        print(f"🎯 Intent Accuracy: {intent_accuracy:.1f}%")
        print(f"🎯 Retrieval Recall: {retrieval_recall:.1f}% (Blueprint Target: >= 85%)")
        print(f"🎯 Safe Refusal Accuracy: {refusal_accuracy:.1f}% (Blueprint Target: >= 90%)")
        print(f"🎯 Faithfulness Grounding: {faithfulness_rate:.1f}% (Blueprint Target: >= 90%)")
        print(f"⚡ Average Latency: {avg_latency:.3f}s (Blueprint Target: < 15.0s)")
        print("=" * 65)

        return summary

if __name__ == "__main__":
    runner = AgriculturalBenchmarkRunner()
    results = runner.run_benchmark()
    with open(config.BASE_DIR / "benchmark_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Benchmark report saved to benchmark_report.json")
