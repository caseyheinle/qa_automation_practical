
## To run the tool from the CLI:

1.  `python main.py --issue <IssueId>`

2. There are two optional arguments that can be passed in: `--git` and `--jira`.

These have default values that are specified in the assignment, `fixtures/git_changes.txt` and `fixtures/jira_issues.json`. If you wish to use alternative files, pass the file path as an argument. e.g. `python main.py --issue <IssueId> --jira my/full/path/to/file.json`

  

## Modifications that I made:

I observed that the provided git_changes.txt file had unnecessary line breaks in the commit message. I updated that formatting for better parsing.

  

## Example output:
Valid IssueId:
`python main.py --issue QA-1234`

output:

    {
    "fields": {
      "customfield_12345": "Test Scope: Regression test: checkout flow with promo code\nLabels: checkout, promocode, regression\nFound 2 recent commit(s) referencing this ticket:\n- 9a1b2c3: QA-1234: Add promo code validation in CheckoutService\n- 7f6e5d4: QA-1234: Refactor cart totals calculation to include promo discounts\nLikely impacted files:\n - tests/cart/cart_totals.unit.spec.js\n - src/checkout/CheckoutService.js\n - tests/checkout/promo/checkout_promo_e2e.spec.js\n - src/cart/CartTotals.js"
    	}
    }

Invalid IssueId:
`python main.py --issue QA-999999`

output:

`Jira issue QA-999999 not found.`
