#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified CLI runner for best-sellers-cache."""

import argparse
import os
import sys

from scrapers import SCRAPER_REGISTRY

def main():
    parser = argparse.ArgumentParser(description="Run bestseller cache scrapers")
    parser.add_argument(
        '--source',
        choices=list(SCRAPER_REGISTRY.keys()) + ['all'],
        default='all',
        help="Source scraper to execute (default: all)"
    )
    parser.add_argument(
        '--output-dir',
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Root directory where static JSON caches are saved"
    )

    args = parser.parse_args()
    output_dir = os.path.abspath(args.output_dir)

    print(f"=== Best Sellers Cache Runner ===")
    print(f"Output Directory: {output_dir}")
    print(f"Target Source:    {args.source}")
    print("=================================")

    if args.source == 'all':
        for name, runner in SCRAPER_REGISTRY.items():
            print(f"\n--- Running: {name} ---")
            try:
                runner(output_dir)
            except Exception as e:
                print(f"ERROR running {name}: {e}")
    else:
        runner = SCRAPER_REGISTRY[args.source]
        print(f"\n--- Running: {args.source} ---")
        runner(output_dir)

    print("\nAll tasks finished successfully.")

if __name__ == '__main__':
    main()
