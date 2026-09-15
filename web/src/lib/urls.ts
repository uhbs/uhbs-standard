/** Site base, e.g. `/uhbs-standard/`. */
export function siteBase(): string {
  return import.meta.env.BASE_URL || "/";
}

/**
 * MkDocs URL under the published site.
 * In Vite dev the mkdocs tree is not served, so we point at GitHub Pages;
 * in production builds we stay on the same host via BASE_URL.
 */
export function mkdocsUrl(path = ""): string {
  const clean = path.replace(/^\//, "");
  if (import.meta.env.DEV) {
    return `https://uhbs.github.io/uhbs-standard/mkdocs/${clean}`;
  }
  return `${siteBase()}mkdocs/${clean}`;
}

/** Asset or root file under the landing base (e.g. llms.txt). */
export function siteUrl(path = ""): string {
  const clean = path.replace(/^\//, "");
  return `${siteBase()}${clean}`;
}

/** Resolve relative landing/mkdocs hrefs so Vite SPA fallback does not swallow them. */
export function resolveHref(href: string): string {
  if (
    !href ||
    href.startsWith("http://") ||
    href.startsWith("https://") ||
    href.startsWith("#") ||
    href.startsWith("mailto:")
  ) {
    return href;
  }
  if (href.startsWith("mkdocs/")) {
    return mkdocsUrl(href.slice("mkdocs/".length));
  }
  return siteUrl(href.replace(/^\.\//, ""));
}
