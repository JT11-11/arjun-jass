> **Note**: This README was generated with AI assistance to provide comprehensive documentation for new collaborators. The content reflects the actual codebase structure and functionality as analyzed from the source code.

# LLM Game Theory Simulation Framework

A comprehensive framework for simulating various game theory scenarios using Large Language Models (LLMs). This project enables researchers and developers to test how different AI models behave in strategic decision-making scenarios, from classic games like Prisoner's Dilemma to complex social and economic games.

## 🎯 Project Overview

This framework simulates multiple game theory scenarios across different LLM providers to analyze AI decision-making patterns. It supports various game types including:

- **Dictator Game**: Tests fairness and altruism in resource allocation
- **Prisoner's Dilemma**: Classic cooperation vs. defection scenarios  
- **Cost Sharing Game**: Team coordination and scheduling decisions
- **Atomic/Non-Atomic Congestion Games**: Resource allocation under constraints
- **Social Context Games**: Decision-making influenced by social factors
- **Hedonic Games**: Coalition formation and preference-based grouping

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

## 📁 Project Structure

```
arjun-jass/
├── main.py                    # Main simulation runner
├── single_game_test.py        # Individual game testing
├── requirements.txt           # Python dependencies
├── config/                    # Game configuration files
│   ├── DictatorGame.csv
│   ├── PrisonnersDilemma.csv
│   ├── CostSharingGame.csv
│   └── ...
├── helper/
│   ├── game/                  # Game implementations
│   │   ├── game.py           # Abstract base class
│   │   ├── dictator_game.py
│   │   ├── prisoner_dilemma.py
│   │   └── ...
│   ├── llm/                  # LLM interface
│   │   └── LLM.py
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

## 🤖 Supported LLM Providers

The framework supports multiple LLM providers through OpenRouter:

- **OpenAI**: GPT-4o, GPT-3.5-turbo
- **Google**: Gemini 2.5 Flash
- **Anthropic**: Claude Sonnet 4
- **Meta**: Llama 3.3, Llama 4 Scout
- **Microsoft**: Phi-3.5 Mini
- **DeepSeek**: DeepSeek R1

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

### Single Game Testing

Use `single_game_test.py` for focused testing:

```python
# Test specific game with custom configuration
python single_game_test.py
```

### Debugging

Enable debug output by modifying the logging level in game implementations. Most games include detailed debug prints for troubleshooting.

## 📈 Analysis and Visualization

The `helper/data/` directory contains utilities for:

- **Data indexing** and aggregation
- **Statistical analysis** of results
- **Visualization** of decision patterns

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

[Add your license information here]

## 🙋‍♂️ Support

For questions, issues, or contributions:

- Create an issue in the repository
- Contact the maintainers
- Check existing documentation

---


