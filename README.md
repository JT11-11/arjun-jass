> **Note**: This README was generated with AI assistance to provide comprehensive documentation for new collaborators. The content reflects the actual codebase structure and functionality as analyzed from the source code.

# LLM Game Theory Simulation Framework

A comprehensive framework for simulating various game theory scenarios using Large Language Models (LLMs). This project enables researchers and developers to test how different AI models behave in strategic decision-making scenarios, from classic games like Prisoner's Dilemma to complex social and economic games.

## 🎯 Project Overview

This framework simulates multiple game theory scenarios across different LLM providers to analyze AI decision-making patterns. It supports various game types including:

- **Dictator Game**: Tests fairness and altruism in resource allocation
- **Prisoner's Dilemma**: Classic cooperation vs. defection scenarios  
- **Cost Sharing Game**: Team coordination and scheduling decisions
- **Hedonic Games**: Social group formation with friend/enemy preferences
- **Gen Coalition Games**: Resource allocation between personal and friend benefits
- **Atomic/Non-Atomic Congestion Games**: Resource allocation under constraints
- **Social Context Games**: Decision-making influenced by social factors

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key (for LLM access)
- Required Python packages (see `requirements.txt`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arjun-jass
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```bash
   OPEN_ROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. **Run the simulation**
   ```bash
   python main.py
   ```

5. **Test altruism injection** (optional)
   ```bash
   python test_all_scenarios.py
   ```

## 📁 Project Structure

```
arjun-jass/
├── main.py                    # Main simulation runner
├── test_all_scenarios.py      # Comprehensive testing with altruism injection
├── single_game_test.py        # Individual game testing
├── requirements.txt           # Python dependencies
├── config/                    # Game configuration files
│   ├── DictatorGame.csv
│   ├── PrisonnersDilemma.csv
│   ├── CostSharingGame.csv
│   ├── HedonicGame.csv
│   ├── GenCoalition.csv
│   └── ...
├── helper/
│   ├── game/                  # Game implementations
│   │   ├── game.py           # Abstract base class
│   │   ├── dictator_game.py
│   │   ├── prisoner_dilemma.py
│   │   ├── hedonic_game.py
│   │   ├── gen_coalition.py
│   │   └── ...
│   ├── llm/                  # LLM interface
│   │   ├── LLM.py
│   │   └── AltruismInjection.py
│   └── data/                 # Data processing utilities
│       ├── dictator_indexer.py
│       └── ...
└── data/                     # Output CSV files (created at runtime)
```

## 🎮 Supported Games

### 1. Dictator Game
Tests fairness in resource allocation scenarios where one player controls all resources.

**Configuration**: `config/DictatorGame.csv`
- **Scenarios**: Single recipient, multiple recipients (optional/mandatory)
- **Variables**: Endowment amount, team size, work contribution, project context
- **Output**: Keep vs. donate percentages with reasoning

### 2. Prisoner's Dilemma
Classic cooperation vs. defection game with iterated rounds.

**Configuration**: `config/PrisonnersDilemma.csv`
- **Features**: Multiple rounds, different opponent strategies
- **Payoff Matrix**: Configurable reward structure
- **Output**: Move history, reasoning, cumulative scores

### 3. Cost Sharing Game
Team coordination scenarios involving scheduling and resource allocation.

**Configuration**: `config/CostSharingGame.csv`
- **Scenarios**: Early booking vs. coordinated scheduling
- **Variables**: Team size, relationships, payout structures
- **Output**: Choice made (individual vs. team benefit)

### 4. Hedonic Games
Social group formation based on friend/enemy preferences and utility maximization.

**Configuration**: `config/HedonicGame.csv`
- **Scenarios**: Agent deciding to STAY in current group or LEAVE to be alone
- **Variables**: Friend/enemy relationships, group compositions, utility weights
- **Output**: Decision (STAY/LEAVE) with altruism score calculation
- **Features**: Mathematical altruism scoring based on personal sacrifice vs. friends' benefit

### 5. Gen Coalition Games
Resource allocation between personal benefit and helping friends in coalition scenarios.

**Configuration**: `config/GenCoalition.csv`
- **Scenarios**: Allocate effort between projects with different personal/friend payoffs
- **Variables**: Personal gain rates, friend benefit rates, coalition structures
- **Output**: Allocation percentages and distance to different behavioral models
- **Features**: Comparison against Selfish (SF), Equal (EQ), and Altruistic (AL) models

## 🤖 Supported LLM Providers

The framework supports multiple LLM providers through OpenRouter:

- **OpenAI**: GPT-4o, GPT-3.5-turbo
- **Google**: Gemini 2.5 Flash
- **Anthropic**: Claude Sonnet 4
- **Meta**: Llama 3.3, Llama 4 Scout
- **Microsoft**: Phi-3.5 Mini
- **DeepSeek**: DeepSeek R1

## 🧠 Altruism Injection

The framework includes a powerful **Altruism Injection** feature that modifies LLM behavior to be more cooperative and other-focused:

### **AltruismInjection Class**
- **Location**: `helper/llm/AltruismInjection.py`
- **Function**: Wraps any LLM to inject altruistic prompting
- **Effect**: Makes LLMs prioritize fairness, cooperation, and others' well-being

### **Usage Example**
```python
from helper.llm.LLM import LLM
from helper.llm.AltruismInjection import AltruismInjection

# Normal LLM
normal_llm = LLM("openai/gpt-3.5-turbo")

# Altruistic LLM (same model, different behavior)
altruistic_llm = AltruismInjection("openai/gpt-3.5-turbo")
```

### **Proven Impact**
- **Gen Coalition**: 55.4% more altruistic behavior
- **Dictator Game**: 75% increase in generosity (40% → 70% donation)
- **Hedonic Games**: 8.3% increase in group cooperation
- **Consistent**: Strong altruistic patterns across all game types

### **Testing Altruism**
```bash
# Run comprehensive altruism testing
python test_all_scenarios.py
```

## 🔧 Configuration

### Game Configuration Files

Each game type has a corresponding CSV configuration file in the `config/` directory. These files define:

- **Simulation parameters**: Number of rounds, scenarios
- **Game variables**: Payouts, team sizes, relationships
- **Prompt templates**: Customizable prompts for each scenario

### Example Configuration (Dictator Game)

```csv
simulate_rounds,scenario_type,endowment,num_recipients,work_contribution,project_context,team_relationship,prompt_template
5,SINGLE_RECIPIENT,200,1,equal,software development project,colleagues,"You have just completed a {project_context}..."
```

## 🏗️ Architecture

### Core Components

1. **Game Abstract Class** (`helper/game/game.py`)
   - Base class that all games must inherit from
   - Defines the `simulate_game()` method interface

2. **LLM Interface** (`helper/llm/LLM.py`)
   - Unified interface for different LLM providers
   - Supports both synchronous and asynchronous requests
   - Handles structured response parsing

3. **Main Runner** (`main.py`)
   - Orchestrates game execution across multiple LLMs
   - Manages configuration loading and result collection
   - Handles parallel execution and error recovery

### Data Flow

```
Configuration CSV → Game Instance → LLM Requests → Results → CSV Output
```

## 📊 Output and Results

### CSV Output Format

Each game generates structured CSV files with:

- **LLM identification**: Model name and provider
- **Game parameters**: Scenario details, configuration values
- **Decisions made**: Numerical choices and reasoning
- **Metadata**: Timestamps, round numbers, etc.

### Example Output Structure

```csv
llm_name,response,scenario_type,endowment,num_recipients,keep,donate
openai/chatgpt-4o-latest,"I believe in fair distribution...",SINGLE_RECIPIENT,200,1,60,40
```

## 🛠️ Development Guide

### Adding a New Game

1. **Create game class** in `helper/game/`
   ```python
   from helper.game.game import Game
   
   class MyNewGame(Game):
       def __init__(self, config: Dict, llms: List[LLM]):
           # Initialize game parameters
           
       async def simulate_game(self):
           # Implement game logic
   ```

2. **Add configuration file** in `config/`
   - Define CSV structure with required parameters
   - Include prompt templates and scenario variations

3. **Update main.py**
   - Add game to `game_info` list
   - Ensure proper import statements

### Customizing LLM Behavior

The `LLM` class supports:

- **Custom response formats** using Pydantic models
- **Asynchronous requests** for better performance
- **History management** for multi-turn conversations
- **Error handling** and fallback responses

## 🧪 Testing

### Comprehensive Testing

Use `test_all_scenarios.py` for full testing across all games and scenarios:

```bash
# Test all scenarios with normal vs altruistic LLMs
python test_all_scenarios.py
```

**Features:**
- Tests all 27+ scenarios across Hedonic and Gen Coalition games
- Compares normal vs altruistic LLM behavior
- Provides detailed statistics and impact measurements
- Generates comprehensive CSV reports

### Single Game Testing

Use `single_game_test.py` for focused testing:

```bash
# Test specific game with custom configuration
python single_game_test.py
```

### Altruism Testing

Test the altruism injection feature:

```python
from helper.llm.LLM import LLM
from helper.llm.AltruismInjection import AltruismInjection

# Compare normal vs altruistic behavior
normal_llm = LLM("openai/gpt-3.5-turbo")
altruistic_llm = AltruismInjection("openai/gpt-3.5-turbo")
```

### Debugging

Enable debug output by modifying the logging level in game implementations. Most games include detailed debug prints for troubleshooting.

## ⚡ Performance Features

### **Parallel Processing**
- **Threading**: All games use `ThreadPoolExecutor` for parallel LLM calls
- **Speed**: 3-5x faster execution when testing multiple LLM models
- **Scalability**: Performance scales with number of LLM providers

### **Mathematical Altruism Scoring**
- **Hedonic Games**: Implements formal altruism score calculation
- **Formula**: `max(0, (personal_sacrifice / friends_benefit) - friends_harm)`
- **Research-Grade**: Mathematically rigorous altruism measurement

### **Comprehensive Data Collection**
- **CSV Output**: Structured data for all games and scenarios
- **Metadata**: LLM names, timestamps, configuration details
- **Analysis-Ready**: Data formatted for statistical analysis

## 📈 Analysis and Visualization

The `helper/data/` directory contains utilities for:

- **Data indexing** and aggregation
- **Statistical analysis** of results
- **Visualization** of decision patterns
- **Altruism score analysis** and comparison

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement your changes**
4. **Add tests and documentation**
5. **Submit a pull request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters
- Include docstrings for public methods
- Maintain consistent error handling

## 📝 License

All Rights Reserve

---


