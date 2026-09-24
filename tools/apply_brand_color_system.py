#!/usr/bin/env python3
"""
apply_brand_color_system.py
Applies the approved Tirumala brand color system across all pages:
- Official Brand Accents: Deep Navy #0B3D91 & Sky Blue #2EA8F2
- Heading text: Solid dark navy/slate #0F172A (removes neon purple/pink gradients & midnight violet #12023B)
- Approved Sidebar CTA Gradient: linear-gradient(135deg, #0B3D91 0%, #2EA8F2 100%)
- Neutral Family: Consistent Tailwind Slate (#0F172A, #334155, #475569, #64748B, #E2E8F0, #F8FAFC)
- Preserves semantic colors: rating stars (#FBBC04), success (#10B981), warning (#F59E0B), error (#EF4444), platform social icons.
"""

import os
import glob
import re

def process_html_content(content, filename=""):
    original = content
    
    # 1. Ensure tcs-tokens.css link is included before tcs-interactions.css in <head>
    if '<link href="./css/tcs-interactions.css" rel="stylesheet"/>' in content:
        if '<link href="./css/tcs-tokens.css" rel="stylesheet"/>' not in content:
            content = content.replace(
                '<link href="./css/tcs-interactions.css" rel="stylesheet"/>',
                '<link href="./css/tcs-tokens.css" rel="stylesheet"/><link href="./css/tcs-interactions.css" rel="stylesheet"/>'
            )
    elif '<link href="./css/tcs-interactions.css" rel="stylesheet" />' in content:
        if '<link href="./css/tcs-tokens.css" rel="stylesheet" />' not in content:
            content = content.replace(
                '<link href="./css/tcs-interactions.css" rel="stylesheet" />',
                '<link href="./css/tcs-tokens.css" rel="stylesheet" /><link href="./css/tcs-interactions.css" rel="stylesheet" />'
            )

    # 2. In-article content theme variables & styles
    content = content.replace('--content-theme-color: #14b8a6;', '--content-theme-color: var(--tcs-primary, #0B3D91);')
    content = content.replace('--content-theme-color-hover: #0d9488;', '--content-theme-color-hover: var(--tcs-accent, #2EA8F2);')
    content = content.replace('border: 1px solid #7dd3c7;', 'border: 1px solid var(--tcs-accent-border, #BAE6FD);')
    
    # Table top bar in article style
    content = content.replace('height: 3px;\n          background: #14b8a6;', 'height: 3px;\n          background: var(--tcs-primary, #0B3D91);')
    content = content.replace('height: 3px;\r\n          background: #14b8a6;', 'height: 3px;\r\n          background: var(--tcs-primary, #0B3D91);')
    content = content.replace('background: #14b8a6;', 'background: var(--tcs-primary, #0B3D91);')
    content = content.replace('border-left-color: #14b8a6;', 'border-left-color: var(--tcs-accent, #2EA8F2);')
    content = content.replace('background: #f0fdfa;', 'background: var(--tcs-surface-hover, #F0F8FF);')

    # Article headings color #1f1646
    content = content.replace('color: #1f1646;', 'color: var(--tcs-text-heading, #0F172A);')

    # 3. Hero and H1/H2 Midnight violet replacement (#12023B -> #0F172A)
    content = content.replace('text-[#12023B]', 'text-[#0F172A]')

    # 4. Remove neon purple/pink heading gradient spans
    content = content.replace('<span class="bg-gradient-to-r from-[#5C3BFF] via-[#7052FF] to-[#FF4ED0] bg-clip-text text-transparent">', '<span>')
    content = content.replace('<span class="bg-gradient-to-r from-[#6A49FF] to-[#EA5FD6] bg-clip-text text-transparent">', '<span>')
    content = content.replace('class="bg-gradient-to-r from-[#5C3BFF] via-[#7052FF] to-[#FF4ED0] bg-clip-text text-transparent"', '')
    content = content.replace('class="bg-gradient-to-r from-[#6A49FF] to-[#EA5FD6] bg-clip-text text-transparent"', '')

    # 5. Decorative underline accent lines (Keep selective approved gradient #0B3D91 -> #2EA8F2)
    content = content.replace('bg-gradient-to-r from-[#5C3BFF] via-[#7052FF] to-[#FF4ED0]', 'bg-gradient-to-r from-[#0B3D91] to-[#2EA8F2]')
    content = content.replace('bg-gradient-to-r from-[#6A49FF] to-[#EA5FD6]', 'bg-gradient-to-r from-[#0B3D91] to-[#2EA8F2]')

    # 6. Hero background blur circles & card top accent line
    content = content.replace('bg-emerald-100/20', 'bg-sky-100/20')
    content = content.replace('bg-teal-100/20', 'bg-sky-100/20')
    content = content.replace('bg-emerald-500/60', 'bg-[#0B3D91]/60')

    # 7. Breadcrumbs
    content = content.replace('hover:text-emerald-600', 'hover:text-[#2EA8F2]')
    content = content.replace('text-emerald-600 font-medium', 'text-[#0B3D91] font-medium')
    content = content.replace('text-emerald-600', 'text-[#0B3D91]')

    # 8. Sidebar CTA and cards
    # Top accent line
    content = content.replace('bg-gradient-to-r from-sky-500 via-teal-400 to-emerald-400', 'bg-gradient-to-r from-[#0B3D91] to-[#2EA8F2]')
    # CTA Button
    content = content.replace(
        'bg-gradient-to-r from-sky-600 to-teal-600 hover:from-sky-700 hover:to-teal-700',
        'bg-gradient-to-r from-[#0B3D91] to-[#2EA8F2] hover:from-[#082C6A] hover:to-[#1A96E0]'
    )
    # Why Choose Tirumala checkmark boxes
    content = content.replace(
        'bg-teal-100/90 border border-teal-300 flex items-center justify-center shrink-0 text-teal-700',
        'bg-[#F0F8FF] border border-[#BAE6FD] flex items-center justify-center shrink-0 text-[#0B3D91]'
    )
    content = content.replace(
        'bg-teal-100 border border-teal-300 flex items-center justify-center shrink-0 text-teal-700',
        'bg-[#F0F8FF] border border-[#BAE6FD] flex items-center justify-center shrink-0 text-[#0B3D91]'
    )

    # 9. FAQ Section inline styles
    content = content.replace('background: #0d9488;', 'background: var(--tcs-primary, #0B3D91);')
    content = content.replace('border-color: #0d9488;', 'border-color: var(--tcs-accent, #2EA8F2);')
    content = content.replace('border-color: #0d9488 !important;', 'border-color: var(--tcs-primary, #0B3D91) !important;')
    content = content.replace('box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.07);', 'box-shadow: 0 0 0 3px rgba(46, 168, 242, 0.10);')
    content = content.replace('box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.08) !important;', 'box-shadow: 0 0 0 3px rgba(11, 61, 145, 0.08) !important;')
    content = content.replace('color: #0f766e;', 'color: var(--tcs-primary, #0B3D91);')
    content = content.replace('color: #0d9488;', 'color: var(--tcs-primary, #0B3D91);')

    # 10. Related Services Section pills hover & active state
    content = content.replace(
        'hover:border-teal-500 hover:bg-teal-50/60 hover:text-teal-700',
        'hover:border-[#2EA8F2] hover:bg-[#F0F8FF] hover:text-[#0B3D91]'
    )
    content = content.replace(
        'hover:border-teal-500 hover:bg-teal-50 hover:text-teal-700',
        'hover:border-[#2EA8F2] hover:bg-[#F0F8FF] hover:text-[#0B3D91]'
    )
    content = content.replace(
        'border border-teal-200 bg-teal-50 px-3.5 py-2 text-[13px] font-medium text-teal-800',
        'border border-[#BAE6FD] bg-[#F0F8FF] px-3.5 py-2 text-[13px] font-medium text-[#0B3D91]'
    )
    content = content.replace(
        'border-teal-200 bg-teal-50',
        'border-[#BAE6FD] bg-[#F0F8FF]'
    )
    content = content.replace('text-teal-800', 'text-[#0B3D91]')

    # 11. Secondary pages "Why Choose" boxes (e.g. patent-registration.html)
    content = re.sub(r'bg-emerald-50\s+ring-1\s+ring-emerald-200(?:/\d+)?', 'bg-[#F0F8FF] ring-1 ring-[#BAE6FD]', content)
    content = content.replace(
        'text-emerald-700 bg-emerald-50 border border-emerald-300 hover:bg-emerald-100',
        'text-[#0B3D91] bg-[#F0F8FF] border border-[#BAE6FD] hover:bg-[#0B3D91] hover:text-white'
    )
    content = content.replace('bg-emerald-500', 'bg-[#0B3D91]')
    content = content.replace('hover:border-emerald-500', 'hover:border-[#2EA8F2]')
    content = content.replace('border-l-emerald-500', 'border-l-[#0B3D91]')
    content = content.replace('border-r-emerald-500', 'border-r-[#0B3D91]')
    content = content.replace('border-t-emerald-500', 'border-t-[#0B3D91]')
    content = content.replace('border-b-emerald-500', 'border-b-[#0B3D91]')
    content = content.replace('border-emerald-500', 'border-[#0B3D91]')
    content = content.replace('border-emerald-300', 'border-[#BAE6FD]')
    content = content.replace('border-emerald-200', 'border-[#BAE6FD]')
    content = content.replace('via-emerald-300', 'via-[#2EA8F2]')
    content = content.replace('shadow-emerald-500/20', 'shadow-[#0B3D91]/10')
    content = content.replace('shadow-emerald-500/10', 'shadow-[#0B3D91]/10')
    content = content.replace('shadow-emerald-500', 'shadow-[#0B3D91]')
    content = content.replace('bg-emerald-50/60', 'bg-[#F0F8FF]/60')
    content = content.replace('bg-emerald-50', 'bg-[#F0F8FF]')
    content = content.replace('text-emerald-700', 'text-[#0B3D91]')
    content = content.replace('hover:bg-emerald-100', 'hover:bg-[#F0F8FF]')
    content = content.replace('hover:bg-emerald-600', 'hover:bg-[#082C6A]')
    content = content.replace('focus:ring-emerald-500/20', 'focus:ring-[#0B3D91]/20')
    content = content.replace('focus-visible:ring-emerald-500', 'focus-visible:ring-[#0B3D91]')
    content = content.replace('focus:ring-emerald-500', 'focus:ring-[#0B3D91]')
    content = content.replace('focus:border-emerald-500', 'focus:border-[#0B3D91]')

    # UI Gradients (replace legacy emerald/teal with brand gradient #0B3D91 to #2EA8F2)
    content = content.replace('from-emerald-600 to-teal-600', 'from-[#0B3D91] to-[#2EA8F2]')
    content = content.replace('from-emerald-500 to-teal-600', 'from-[#0B3D91] to-[#2EA8F2]')
    content = content.replace('from-emerald-500 to-emerald-600', 'from-[#0B3D91] to-[#2EA8F2]')
    content = content.replace('from-emerald-500', 'from-[#0B3D91]')
    content = content.replace('to-teal-600', 'to-[#2EA8F2]')
    content = content.replace('to-teal-500', 'to-[#2EA8F2]')
    content = content.replace('to-emerald-600', 'to-[#2EA8F2]')

    # 12. Lead Gen / Consult form focus states
    content = content.replace(
        'focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10',
        'focus:border-[#0B3D91] focus:ring-4 focus:ring-[#0B3D91]/10'
    )
    content = content.replace(
        'focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10',
        'focus-within:border-[#0B3D91] focus-within:ring-4 focus-within:ring-[#0B3D91]/10'
    )

    # 13. Footer link hover (keep social icons untouched)
    content = content.replace('group-hover:text-blue-600', 'group-hover:text-[#2EA8F2]')
    content = content.replace('group-hover:w-full bg-blue-600', 'group-hover:w-full bg-[#2EA8F2]')

    return content

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(root_dir, '*.html')
    files = [f for f in glob.glob(pattern) if not f.endswith('_raw.html')]
    
    # Also include template files
    template_files = glob.glob(os.path.join(root_dir, 'templates', '**', '*.html'), recursive=True)
    all_targets = files + template_files

    print(f"Total HTML files to process: {len(all_targets)}")
    modified_count = 0

    for filepath in all_targets:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content = process_html_content(content, os.path.basename(filepath))

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified_count += 1

    print(f"Successfully applied brand color system to {modified_count} / {len(all_targets)} files.")

if __name__ == '__main__':
    main()
