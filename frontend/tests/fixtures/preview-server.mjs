import { readFileSync, existsSync } from "node:fs";
import { createServer } from "node:http";
import { registerHooks } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = resolve(HERE, "../..");
const PORT = Number(process.env.PREVIEW_PORT ?? 18767);

// Resolve aliases and extensionless TypeScript imports for Node.
function resolveSource(specifier, parentURL) {
  let target = null;
  if (specifier.startsWith("@/")) target = join(FRONTEND, specifier.slice(2));
  if (specifier.startsWith(".") && parentURL?.startsWith("file:")) {
    target = fileURLToPath(new URL(specifier, parentURL));
  }
  if (!target) return null;

  const candidates = [
    target,
    `${target}.ts`,
    `${target}.tsx`,
    join(target, "index.ts"),
    join(target, "index.tsx"),
  ];
  const found = candidates.find(candidate => existsSync(candidate));
  return found ? pathToFileURL(found).href : null;
}

registerHooks({
  resolve(specifier, context, nextResolve) {
    const source = resolveSource(specifier, context.parentURL);
    return source ? { url: source, shortCircuit: true } : nextResolve(specifier, context);
  },
  load(url, context, nextLoad) {
    if (url.endsWith(".tsx") || url.endsWith(".ts")) {
      const source = readFileSync(fileURLToPath(url), "utf8");
      const output = ts.transpileModule(source, {
        compilerOptions: {
          target: ts.ScriptTarget.ES2022,
          module: ts.ModuleKind.ESNext,
          moduleResolution: ts.ModuleResolutionKind.Bundler,
          jsx: ts.JsxEmit.ReactJSX,
          esModuleInterop: true,
        },
        fileName: fileURLToPath(url),
      }).outputText;
      return { format: "module", source: output, shortCircuit: true };
    }

    if (url.endsWith(".css")) {
      // The preview is isolated, so class names stay unscoped.
      return {
        format: "module",
        source:
          "export default new Proxy({}, { get: (_target, key) => typeof key === 'string' ? key : undefined });",
        shortCircuit: true,
      };
    }

    return nextLoad(url, context);
  },
});

const moduleCss = readFileSync(
  join(FRONTEND, "components/recommend/recommend.module.css"),
  "utf8",
).replaceAll(":global(.combo-wrap)", ".combo-wrap");

const globalsCss = readFileSync(join(FRONTEND, "app/globals.css"), "utf8");
const rootTokens = globalsCss.match(/:root\s*\{([\s\S]*?)\}/)?.[1] ?? "";

const previewCss = `
:root {${rootTokens}}
* { box-sizing: border-box; }
html { font-size: 16px; }
body {
  margin: 0;
  padding: 24px 18px;
  color: var(--foreground);
  background: var(--background);
  font-family: var(--font-system);
  font-size: 1rem;
  line-height: 1.5;
}
h2 { margin: 0; color: var(--card-foreground); font-weight: 500; line-height: 1.2; }
.preview-shell { width: 100%; max-width: 1100px; margin: 0 auto; padding: 0 24px; }
${moduleCss}
`;

const { createElement } = await import("react");
const { renderToStaticMarkup } = await import("react-dom/server");
const { default: UniversityCardPreview } = await import("./UniversityCardPreview.tsx");

const body = renderToStaticMarkup(createElement(UniversityCardPreview));
const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>University card preview</title>
<style>${previewCss}</style>
</head>
<body>
${body}
<script>
// Keep fake fixture links inside the harness.
document.addEventListener("click", event => {
  const link = event.target.closest("a");
  if (!link) return;
  event.preventDefault();
  document.documentElement.dataset.harnessLink = link.getAttribute("href");
});
</script>
</body>
</html>`;

createServer((_request, response) => {
  response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  response.end(html);
}).listen(PORT, "127.0.0.1", () => {
  console.log(`Card preview ready at http://127.0.0.1:${PORT}`);
});
