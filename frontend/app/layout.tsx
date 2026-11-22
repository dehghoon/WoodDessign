import Script from 'next/script';
import type {ReactNode} from 'react';
import './globals.css';
import '../public/design-system/linkoteq-shell-v1.css';
export default function Layout({children}:{children:ReactNode}){return <html lang="en"><body><Script src="https://www.linkoteq.com/design-system/linkoteq-header-v1.js" strategy="afterInteractive" /><div dangerouslySetInnerHTML={{__html: '<linkoteq-header></linkoteq-header>'}} />{children}</body></html>}
