# Agent Internal World Model

## Core rule
WORLD LAB must never equate simulation ground truth with what an individual knows.
The world contains reality. Agents contain partial, noisy, learned models of reality.

## Three layers

### 1. World truth
The authoritative simulation state. It is not automatically visible to agents.

### 2. Perception
Agents receive observations generated from situation, access, attention, relationships, communication, institutions, timing and noise.
Two agents can therefore observe different evidence about the same event.

### 3. Internal model
Each agent maintains beliefs, memories, expectations, perceived opportunities, perceived risks, knowledge gaps and hypotheses. The model can be incomplete or wrong.

## Thinking loop
World -> Perception -> Memory -> Belief update -> Goals/needs/values -> Candidate actions -> Consequence estimation -> Decision -> Action -> World change -> Feedback -> Learning

## Discovery
New knowledge can emerge through observation, experimentation, conversation, teaching, imitation, mistakes, unexpected consequences and institutional learning.

## Anti-cheating rule
Agent decision functions must not silently query hidden ground truth. Debugging and research tools may inspect ground truth, but cognition must use an explicit information boundary.

## Realism boundary
This is not a claim of consciousness. It is an inspectable mechanism for bounded knowledge, learning and decision-making. More sophisticated cognition must be evaluated against empirical evidence.

## Long-term direction
The objective is not to make agents recite stored facts. Agents should increasingly construct, revise and act on internal models while constrained by the world, experience, resources and social environment.