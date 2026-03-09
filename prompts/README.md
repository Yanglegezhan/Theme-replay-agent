# Prompt Templates

This directory contains prompt templates for LLM analysis.

## Templates

- `market_intent.md` - Market capital intent analysis prompt
- `emotion_cycle.md` - Emotion cycle detection prompt
- `sustainability.md` - Theme sustainability evaluation prompt
- `trading_advice.md` - Trading advice generation prompt

## Usage

Templates use Jinja2 syntax for variable substitution. Variables are provided by the ContextBuilder and rendered by the PromptEngine.

## Template Structure

Each template should include:
1. Role definition (persona)
2. Task description
3. Input data format
4. Analysis dimensions
5. Output format specification
