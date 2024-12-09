# RPG Content Generator - README

This project provides a GUI-based tool for generating rich and diverse RPG content (items, NPCs, locations, etc.) influenced by various thematic contexts. It uses the OpenAI GPT API under the hood to produce structured, JSON-validated results, suitable for D&D 3.5e and other fantasy role-playing settings.

## Features
- **Category and Context Browsing:** Select from structured categories (e.g., "Weapons & Armor", "Potions", "NPC types") and thematic contexts (e.g., "Dark & Mystical", "Aquatic & Coastal") to shape your generated content.
- **Schema Validation:** Content is generated according to a JSON schema, ensuring consistent formatting and fields (name, description, etc.).
- **Campaign-Ready:** Add your own campaign-specific notes, system, setting, and level range.
- **Multiple Output Modes:** Results can be displayed as plain text, Markdown, styled (3.5e-like), or raw JSON.
- **Export Options:** Export generated results and detailed statblocks as JSON logs or CSV tables for future reference.

## Prerequisites
- **Python 3.8+**  
- **Poetry** or **pip** for package management
- An OpenAI API key (if using GPT models)

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/rpg-content-generator.git
   cd rpg-content-generator
   ```

2. **Install Dependencies:**
   We recommend using a virtual environment.

   Using [Poetry](https://python-poetry.org/):
   ```bash
   poetry install
   ```
   
   OR using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Your OpenAI API Key:**
   - Open `src/config/config.json`.
   - Under `"gpt-api"`, replace the `"api-key"` value with your actual OpenAI API key. For example:
     ```json
     {
       "gpt-api": {
         "api-key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
       },
       ...
     }
     ```

   This key is required for the GPT integration to function.

4. **(Optional) Adjust Configurations:**
   - Modify `"default_system"` and `"default_setting"` in `config.json` if you want different defaults for the RPG system (e.g., D&D 5e) or setting.
   - Adjust `"max-tokens"`, `"temperature"`, `"models"`, and other `"app-settings"` as desired.

5. **Data & Resources:**
   - The project includes sample category and context files in `./src/resources/`.  
   - By default, `dnd_categories.json` and `dnd_contexts.json` are used, but you can switch to `starwars_categories.json` / `starwars_contexts.json` or other provided files.
   - You can add your own `*_categories.json` and `*_contexts.json` files to `src/resources` and select them via the GUI.

## Running the Application
From the project root:
```bash
poetry run python src/main.py
```
OR, if using pip and a standard venv:
```bash
python src/main.py
```

The GUI will launch.

## How to Use
1. **Select Categories & Contexts Files (Optional):**  
   In the left panel, choose which categories and contexts file you want to load.  
   - For example, choose `dnd_categories.json` and `dnd_contexts.json` for D&D 3.5e inspired content.

2. **Browse Categories:**
   - Expand and collapse the category tree to find the type of content you want to generate (e.g., "Items" → "Weapons & Armor" → "Melee Weapons" → "Simple Melee Weapon").
   - Check the leaf nodes you want. For example, checking "Simple Melee Weapon" sets that as your content type.

3. **Browse Contexts:**
   - Similarly, in the contexts section, select thematic contexts that will influence the generated content (e.g., "Darkness & Gloom" → "Dark", "Haunted").
   - Check multiple contexts to combine them.

4. **Adjust Options:**
   - In the Options panel (right side), set the number of results, level range, detail display mode, and add any custom campaign notes.
   - Specify the RPG system and setting in the fields provided.

5. **Generate Content:**
   - Click the "Generate" button.  
   - The tool will query the GPT API and produce results according to the selected categories, contexts, and schema.
   - Results appear in a table. Selecting a row shows a preview on the right.

6. **Detailed Statblock:**
   - After selecting a generated result, click "More Info" to request a full statblock expansion.  
   - This queries the LLM again for a more detailed JSON output, displayed in the chosen format.

7. **Exporting Results:**
   - "Export Preview" saves the detailed JSON output for each item in a log directory.
   - "Export Table" saves a CSV table with the current results for quick reference.

## Customization
- **Adding New Schemas:**  
  The tool can generate schemas dynamically or use a fallback default schema. If you want to create a custom schema, modify `src/resources/default_schema.json`.
  
- **New Settings or Systems:**
  Update `config.json` to change defaults or edit `AppState` in `models/state.py` to store additional data.

- **Additional Contexts/Categories:**
  Add new JSON files in `src/resources/` named `xxx_categories.json` and `xxx_contexts.json`. The app will detect them, and you can select them from the dropdown.

## Troubleshooting
- **No Results Generated:**  
  Check your API key and OpenAI usage limits. Also verify that you've selected at least one valid category type and one context.
  
- **Validation Errors:**  
  If the schema is too strict or the model fails to produce valid JSON, the fallback schema is used. Try adjusting prompts or disabling schema validation in `config.json`.

- **Performance Issues:**
  Generating large numbers of results or using complex contexts might be slow. Increase `llm_retry_delay` or reduce `num_results` if needed.

## License
Just use it and make sure you tell people who built it - not you :] Me, I did. I built it. If you extend it, then WE built it. We is the mirror-verse of ME!

---

With these steps and configurations, you should be able to install, run, and use the RPG Content Generator to enrich your tabletop RPG sessions with tailored content. Enjoy your adventures!
