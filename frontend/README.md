# Wood standalone frontend

Extracted from Main-website at the commit recorded in MIGRATION.md. The Python API stays at the repository root; this directory owns the website and interactive member viewer.

Vercel: create a **separate frontend project**, connect this repository, and set Root Directory to `frontend`. Keep the existing Python API project unchanged. Copy the canonical website's public Supabase URL and anon key (never its service-role key).

Run `npm ci`, `npm run typecheck`, and `npm run build`.

The canonical public route is `/tools/wood-design` on www.linkoteq.com. Access Manager and calculation requests remain on the canonical API with the user's Bearer token. These components keep their existing access checks and Beta disclosures.

## Cutover

Do not change production until the preview builds and signed-in/unauthenticated/denied user flows pass. Preview host storage is separate from the main website, so a login on the main domain does not log the user into a standalone preview.

To preserve the existing login, configure the main site's **beforeFiles** external rewrites for `/tools/wood-design`, `/tools/wood-design/:path*` and `/_wood-assets/:path*` to this frontend's deployment origin. Do not redirect the browser to the preview domain. Keep existing canonical API routes, header, and login destinations. Retain the current pages for rollback until live verification succeeds.

A future dedicated subdomain requires an explicit cross-origin session handoff; adding DNS alone does not share local-storage sessions.
