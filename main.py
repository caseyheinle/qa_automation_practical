import argparse
import json
import os
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Jira-Git Analysis Agent")
    parser.add_argument('--issue', required=True, help='Jira issue key (e.g., QA-1234)')
    parser.add_argument('--jira', default='fixtures/jira_issues.json', help='Path to Jira issues JSON')
    parser.add_argument('--git', default='fixtures/git_changes.txt', help='Path to git log file')
    return parser.parse_args()

def load_jira_issues(jira_path):
    with open(jira_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def select_jira_issue(issues, key):
    for issue in issues:
        if issue.get('key') == key:
            return issue
    return None

def parse_git_changes(git_path):
    # Each commit starts with "commit <sha> <message>", then "Files changed:", then file lines
    commits = []
    with open(git_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith('commit '):
            # Parse: commit <sha> <message>
            parts = lines[i].strip().split(' ', 2)
            sha = parts[1]
            msg = parts[2] if len(parts) > 2 else ''
            i += 1
            files = []
            # Look for "Files changed:"
            while i < len(lines) and not lines[i].startswith('Files changed:'):
                i += 1
            if i < len(lines) and lines[i].startswith('Files changed:'):
                i += 1
                # Parse file lines until next commit or end
                while i < len(lines) and lines[i].strip() and not lines[i].startswith('commit '):
                    # File line format: <path> (<insertions> insertions, <deletions> deletions)
                    file_path = lines[i].strip().split(' (')[0]
                    files.append(file_path)
                    i += 1
            commits.append({'sha': sha, 'message': msg, 'files': files})
        else:
            i += 1
    return commits

def find_relevant_commits(commits, jira_key, keywords):
    relevant = []
    related_files = set()
    for c in commits:
        if jira_key in c['message']:
            relevant.append(c)
            related_files.update(c['files'])
    # Optionally include likely-related files by matching keywords
    if not relevant:
        for c in commits:
            for kw in keywords:
                if any(kw.lower() in f.lower() for f in c['files']):
                    relevant.append(c)
                    related_files.update(c['files'])
    return relevant, list(related_files)

def generate_analysis(issue, relevant_commits, related_files):
    summary = issue.get('fields', {}).get('summary', 'No summary')
    labels = issue.get('fields', {}).get('labels', [])
    analysis = []
    analysis.append(f"Test Scope: {summary}")
    if labels:
        analysis.append(f"Labels: {', '.join(labels)}")
    else:
        analysis.append("Labels: None")
    if relevant_commits:
        analysis.append(f"Found {len(relevant_commits)} recent commit(s) referencing this ticket:")
        for c in relevant_commits[:3]:
            analysis.append(f"- {c['sha'][:7]}: {c['message']}")
    else:
        analysis.append("No direct commits found referencing this ticket.")
    if related_files:
        analysis.append("Likely impacted files:")
        for f in related_files:
            analysis.append(f"  - {f}")
    else:
        analysis.append("No likely impacted files found.")
    analysis.append("Please review the above changes for targeted testing.")
    # Limit the analysis output to 10 lines ensuring concise and readable results
    return '\n'.join(analysis[:10])

def main():
    args = parse_args()
    issues = load_jira_issues(args.jira)
    issue = select_jira_issue(issues, args.issue)
    if not issue:
        print(f"Jira issue {args.issue} not found.")
        return
    commits = parse_git_changes(args.git)
    # Use summary words and labels as keywords
    summary = issue.get('fields', {}).get('summary', '')
    labels = issue.get('fields', {}).get('labels', [])
    keywords = re.findall(r'\w+', summary) + labels
    relevant_commits, related_files = find_relevant_commits(commits, args.issue, keywords)
    analysis = generate_analysis(issue, relevant_commits, related_files)
    payload = {
        "fields": {
            # This is a hardcoded Jira custom field ID where the analysis will be stored.
            "customfield_12345": analysis
        }
    }
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()