# Question Answering Skill

(No learned rules yet. Rules will be added through the reflection process.)

<answer>Abraham Lincoln</answer>

## Entity Name Normalization
When the answer is a named entity (person, company, country, etc.), use the **most common short form** of the entity's name that is unambiguous in context. For example, use "Apple" rather than "Apple Inc.", "Microsoft" rather than "Microsoft Corporation", or "Einstein" rather than "Albert Einstein" — unless the question explicitly asks for the full formal name.

## Handling Descriptive and Fragment Questions
- When the question is a descriptive phrase (e.g., 'The tallest mountain in the world'), a fragment (e.g., 'He painted the Mona Lisa'), or a fill-in-the-blank, identify the entity being described by matching descriptive keywords to information in the context.
- Answer with the named entity exactly as it appears in the context.
- Briefly state your reasoning (e.g., 'X is described as Y in the context'), then output only the entity name inside <answer>...</answer> tags.
