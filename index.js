/**
 * Qwen Expression Pack – SillyTavern Extension
 * Frontend-only. Talks to the standalone expression-pack container.
 *
 * Backend URL (browser must reach it):
 *   http://localhost:7865
 *   http://<tailscale-magicdns>:7865
 *   https://expression-pack.<docktail-domain>
 *
 * Install: Extensions → Git URL
 *   https://github.com/Jblast94/qwen-expression-pack-generator  (branch: extension)
 */

import {
    extension_settings,
    getContext,
} from '../../../extensions.js';

import {
    eventSource,
    event_types,
    saveSettingsDebounced,
} from '../../../../script.js';

const EXTENSION_NAME = 'st-expression-pack-extension';

const DEFAULT_SETTINGS = {
    backendUrl: 'http://localhost:7865',
    preset: 'full_pack',
    steps: 4,
    guidance: 1.0,
    autoGenerateOnImport: false,
};

let settings = structuredClone(DEFAULT_SETTINGS);

function loadSettings() {
    extension_settings[EXTENSION_NAME] = extension_settings[EXTENSION_NAME] || {};
    Object.assign(settings, DEFAULT_SETTINGS, extension_settings[EXTENSION_NAME]);
}

function saveSettings() {
    extension_settings[EXTENSION_NAME] = { ...settings };
    saveSettingsDebounced();
}

async function getAvatarBlob() {
    const context = getContext();
    const char = context.characters[context.characterId];
    if (!char || !char.avatar) return null;
    const resp = await fetch(`/characters/${char.avatar}`);
    if (!resp.ok) return null;
    return await resp.blob();
}

async function generateExpressionPack() {
    const context = getContext();
    if (context.characterId === undefined || context.characterId === null) {
        toastr.warning('Select a character first.');
        return;
    }

    const char = context.characters[context.characterId];
    const characterName = char.name || 'character';

    toastr.info(
        `Generating expression pack for <b>${characterName}</b>…<br>Usually 1–4 minutes (ZeroGPU queue).`,
        'Qwen Expression Pack',
        { timeOut: 8000, escapeHtml: false }
    );

    try {
        const avatarBlob = await getAvatarBlob();
        if (!avatarBlob) {
            toastr.error('Could not load the character avatar image.');
            return;
        }

        const formData = new FormData();
        formData.append('file', avatarBlob, 'avatar.png');
        formData.append('preset', settings.preset);
        formData.append('steps', String(settings.steps));
        formData.append('guidance', String(settings.guidance));
        formData.append('character_name', characterName);

        const resp = await fetch(`${settings.backendUrl}/api/generate`, {
            method: 'POST',
            body: formData,
        });

        if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`Backend returned ${resp.status}: ${text}`);
        }

        const data = await resp.json();
        console.log('[Qwen Expression Pack] Result:', data);

        const zipUrl = `${settings.backendUrl}${data.sillytavern_url}`;
        const a = document.createElement('a');
        a.href = zipUrl;
        a.download = data.sillytavern_filename || `${characterName}_ST_expressions.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();

        toastr.success(
            `✅ Generated <b>${data.count}</b> expressions for <b>${characterName}</b>.<br><br>` +
            `ZIP downloaded. Use <b>Extensions → Character Expressions → Upload sprite pack (ZIP)</b>.`,
            'Qwen Expression Pack',
            { timeOut: 18000, escapeHtml: false }
        );
    } catch (err) {
        console.error('[Qwen Expression Pack]', err);
        toastr.error(
            `Generation failed: ${err.message}<br><br>` +
            `Is the <b>expression-pack</b> container running and reachable from this browser?<br>` +
            `Backend URL: <code>${settings.backendUrl}</code>`,
            'Qwen Expression Pack',
            { timeOut: 14000, escapeHtml: false }
        );
    }
}

function createSettingsPanel() {
    const html = `
    <div id="qwen-exp-panel" class="qwen-exp-settings">
        <div class="inline-drawer">
            <div class="inline-drawer-toggle inline-drawer-header">
                <b><i class="fa-solid fa-face-smile"></i> Qwen Expression Pack</b>
                <div class="inline-drawer-icon fa-solid fa-circle-chevron-down down"></div>
            </div>
            <div class="inline-drawer-content">
                <div class="qwen-exp-row">
                    <label>Backend URL</label>
                    <input id="qwen-exp-backend" type="text" class="text_pole" value="${settings.backendUrl}" placeholder="http://localhost:7865 or Tailnet/Docktail URL" />
                </div>
                <div class="qwen-exp-row">
                    <label>Preset</label>
                    <select id="qwen-exp-preset" class="text_pole">
                        <option value="standard_28">Standard 28 expressions</option>
                        <option value="nsfw_extra">NSFW / Sensual extra</option>
                        <option value="full_pack">Full Pack (Recommended)</option>
                    </select>
                </div>
                <div class="qwen-exp-row">
                    <label>Inference Steps (1–12)</label>
                    <input id="qwen-exp-steps" type="number" min="1" max="12" class="text_pole" value="${settings.steps}" />
                </div>
                <div class="qwen-exp-row">
                    <label>True Guidance Scale</label>
                    <input id="qwen-exp-guidance" type="number" min="0.5" max="3" step="0.1" class="text_pole" value="${settings.guidance}" />
                </div>
                <div class="qwen-exp-row">
                    <label class="checkbox_label">
                        <input id="qwen-exp-auto" type="checkbox" ${settings.autoGenerateOnImport ? 'checked' : ''} />
                        <span>Auto-generate when a character is edited / imported</span>
                    </label>
                </div>
                <hr style="margin: 12px 0; opacity: 0.3;">
                <button id="qwen-exp-generate" class="menu_button wide_button">
                    <i class="fa-solid fa-wand-magic-sparkles"></i>
                    Generate Expression Pack for Current Character
                </button>
                <p class="qwen-exp-hint">
                    Backend = standalone <b>expression-pack</b> container (Dockhand / any node).<br>
                    Use Tailnet hostname or Docktail URL when not on the same machine.<br>
                    Default: <code>http://localhost:7865</code>
                </p>
            </div>
        </div>
    </div>`;

    const target = document.getElementById('extensions_settings2') || document.getElementById('extensions_settings');
    if (target) target.insertAdjacentHTML('beforeend', html);

    const presetSelect = document.getElementById('qwen-exp-preset');
    if (presetSelect) presetSelect.value = settings.preset;

    document.getElementById('qwen-exp-backend')?.addEventListener('change', (e) => {
        settings.backendUrl = e.target.value.trim().replace(/\/$/, '');
        saveSettings();
    });
    document.getElementById('qwen-exp-preset')?.addEventListener('change', (e) => {
        settings.preset = e.target.value;
        saveSettings();
    });
    document.getElementById('qwen-exp-steps')?.addEventListener('change', (e) => {
        settings.steps = parseInt(e.target.value) || 4;
        saveSettings();
    });
    document.getElementById('qwen-exp-guidance')?.addEventListener('change', (e) => {
        settings.guidance = parseFloat(e.target.value) || 1.0;
        saveSettings();
    });
    document.getElementById('qwen-exp-auto')?.addEventListener('change', (e) => {
        settings.autoGenerateOnImport = e.target.checked;
        saveSettings();
    });
    document.getElementById('qwen-exp-generate')?.addEventListener('click', () => generateExpressionPack());
}

jQuery(async () => {
    loadSettings();
    createSettingsPanel();
    eventSource.on(event_types.CHARACTER_EDITED, () => {
        if (settings.autoGenerateOnImport) {
            setTimeout(() => generateExpressionPack(), 2000);
        }
    });
    console.log('%c[Qwen Expression Pack] Extension loaded', 'color: #a78bfa');
});
