

# Synthetic SFT Data Generator for Game Theory

This directory contains a **synthetic data generator** that creates training data for OpenAI's Supervised Fine-Tuning API. Instead of using your experimental data (which could cause overfitting), this generates **new synthetic examples** that match your exact game formats but teach the model to be 90% altruistic.

## 📁 Directory Structure

```
sft/
├── src/
│   └── generate_synthetic_data.py    # Main synthetic data generator
├── data/
│   ├── sample_training_data.jsonl    # Example generated training data
│   └── sample_preview.txt            # Human-readable example preview
└── README.md                         # This documentation
```

## 🎯 What This Does

Creates synthetic training examples for **ALL your game types**:
- **Dictator Game**: Resource allocation scenarios
- **Prisoner's Dilemma**: Strategic cooperation/defection choices  
- **Cost Sharing Game**: Individual vs team benefit decisions
- **Atomic Congestion Game**: Route selection with congestion effects
- **Hedonic Game**: Social group membership decisions
- **Gen Coalition Game**: Coalition formation and effort allocation
- **Non-Atomic Congestion**: Resource consumption in shared environments
- **Social Context Game**: Ranking and social positioning decisions

## 🚀 Quick Start

### Generate 200 examples (90% altruistic)
```bash
cd sft/
python src/generate_synthetic_data.py --total_examples 200 --altruism_ratio 0.9
```

### Generate with sample file for inspection
```bash
python src/generate_synthetic_data.py \
  --total_examples 200 \
  --altruism_ratio 0.9 \
  --output_file data/training_data.jsonl \
  --sample_file data/sample_preview.txt \
  --sample_size 20
```

### Generate purely altruistic dataset
```bash
python src/generate_synthetic_data.py \
  --total_examples 150 \
  --altruism_ratio 1.0 \
  --output_file data/pure_altruism_training.jsonl
```

## 📊 Example Output

The generator creates JSONL files ready for OpenAI fine-tuning:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "You have just completed a software development project with 2 teammates who are your colleagues. You all contributed equally to the project's success.\n\nThe client has paid $500 directly to you to distribute among the team.\n\nPlease decide how to allocate this payment..."
    },
    {
      "role": "assistant",
      "content": "Reasoning: Fairness and collaboration are essential for team success. Everyone contributed to this software development project, so everyone deserves to benefit. Sharing equitably demonstrates respect for my teammates and builds trust for future projects.\nKeep: 30%\nDonate: 70%"
    }
  ]
}
```

## 🎮 Game Format Matching

Each synthetic example **perfectly matches** your existing game formats:

### Dictator Game Format
- Matches your `DictatorGameAnswerFormat` with reasoning, keep_percent, donate_percent
- Uses same project contexts, team relationships, work contributions
- 90% of examples show generous sharing (20-45% keep, 55-80% donate)

### Prisoner's Dilemma Format  
- Matches your round-based format with payoff matrices
- Uses same choice format (1=Cooperate, 2=Defect)
- 90% of examples choose cooperation with trust-building reasoning

### Cost Sharing Format
- Matches your meeting room scenario structure
- Uses same option format (1=Individual, 2=Team)
- 90% of examples choose team coordination over individual benefit

### And so on for all 8 game types...

## 🔧 Customization Options

### Altruism Ratio
```bash
# 95% altruistic (very generous model)
--altruism_ratio 0.95

# 50% altruistic (balanced model) 
--altruism_ratio 0.5

# 100% altruistic (pure altruism)
--altruism_ratio 1.0
```

### Dataset Size
```bash
# Small dataset for testing
--total_examples 50

# Large dataset for production
--total_examples 500

# Minimum for OpenAI (distributed across 8 game types)
--total_examples 80
```

### Reproducible Generation
```bash
# Use seed for consistent results
--seed 42
```

## 📈 Training Statistics

Example output:
```
✅ Generated 200 synthetic training examples in synthetic_sft_training.jsonl

📊 Synthetic Dataset Statistics:
  Total examples: 200
  Altruistic examples: 180 (90%)
  Non-altruistic examples: 20 (10%)

🎮 By game type:
  atomic_congestion: 25 examples (23 altruistic, 92%)
  cost_sharing_game: 25 examples (23 altruistic, 92%)
  dictator_game: 25 examples (22 altruistic, 88%)
  gen_coalition: 25 examples (22 altruistic, 88%)
  hedonic_game: 25 examples (23 altruistic, 92%)
  non_atomic_congestion: 25 examples (22 altruistic, 88%)
  prisoner_dilemma: 25 examples (23 altruistic, 92%)
  social_context: 25 examples (22 altruistic, 88%)
```

## 🤖 OpenAI Fine-Tuning Integration

### 1. Upload Training Data
```bash
curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="fine-tune" \
  -F file="@synthetic_sft_training.jsonl"
```

### 2. Create Fine-Tuning Job
```bash
curl https://api.openai.com/v1/fine_tuning/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "training_file": "file-abc123",
    "model": "gpt-4.1-nano-2025-04-14"
  }'
```

### 3. Use Your Altruistic Model
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "ft:gpt-4.1-nano-2025-04-14:your-org::model-id",
    "messages": [
      {
        "role": "user", 
        "content": "You have $100 to split between yourself and a teammate. How do you decide?"
      }
    ]
  }'
```

## ✅ Why Synthetic Data?

1. **No Overfitting**: Uses new scenarios, not your experimental data
2. **Perfect Format Matching**: Exactly matches your game structures
3. **Controllable Altruism**: Precise 90% altruistic ratio
4. **Scalable**: Generate as many examples as needed
5. **Diverse**: Varied scenarios, amounts, relationships, contexts
6. **Ready to Use**: Direct JSONL output for OpenAI API

## 🎯 Expected Results

After fine-tuning with this synthetic data, your model should:
- **Consistently choose cooperative strategies** in prisoner's dilemma
- **Share resources generously** in dictator games (typically 60-80% donation)
- **Prioritize team benefit** over individual gain in cost-sharing scenarios
- **Consider collective welfare** in congestion and resource games
- **Demonstrate prosocial reasoning** across all decision contexts

The 90% altruistic ratio ensures the model learns primarily from generous, cooperative examples while maintaining some diversity in decision patterns.

## 🔍 Quality Assurance

- **Format Validation**: All examples match your exact game formats
- **Reasoning Quality**: Thoughtful, contextual explanations for each decision
- **Balanced Distribution**: Equal representation across all 8 game types  
- **Realistic Scenarios**: Plausible contexts, amounts, and relationships
- **Consistent Altruism**: Reliable 90% altruistic behavior patterns
