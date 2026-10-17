# LinkedIn post feed — portfolio setup

LinkedIn profile: https://www.linkedin.com/in/ali-ahmed-khoso/

## What is live now

The website's LinkedIn section reads `data/linkedin-posts.json`. One verified public post
is included initially. Additional public posts can be inserted in the `posts` array.
Card links open the original LinkedIn post. You can edit the feed file on GitHub,
then refresh the live portfolio to display the committed posts.

## Enable automatic daily updates

LinkedIn requires the restricted **r_member_social** read permission to retrieve
personal member posts. A normal LinkedIn login and w_member_social do not grant this permission.
Your LinkedIn developer application must first be approved for this access.

1. Obtain a LinkedIn OAuth member access token with the approved member-post read permission.
2. Obtain your own LinkedIn **person URN**, in `urn:li:person:...` format, from the approved LinkedIn API.
   A profile URL or username is not the same as a person URN.
3. In this GitHub repository open **Settings > Secrets and variables > Actions**.
4. Add `LINKEDIN_ACCESS_TOKEN` as a repository secret containing the token.
5. Add `LINKEDIN_PERSON_URN` as a repository secret containing the person URN.
6. Optional: add `LINKEDIN_API_VERSION` as an Actions variable using a currently
   supported YYYYMM LinkedIn Marketing API version (workflow defaults to `202608`).
7. Run **Actions > Sync LinkedIn posts > Run workflow**.
8. The workflow will repeat daily and commit new public member posts into
   `data/linkedin-posts.json`. GitHub Pages then serves the updated feed.

To inspect the workflow: `.github/workflows/linkedin-sync.yml`.
To inspect the import: `scripts/sync_linkedin.py`.

**Security:** Never paste these credentials in a public website, GitHub issue,
README, or chat. Store access tokens only in GitHub Actions secrets. Tokens expire;
renew them through your approved LinkedIn OAuth process.

If API access is not approved, the workflow safely skips. It cannot bypass
LinkedIn's restrictions or scrape posts.

## Add more posts manually while awaiting approval

Open `data/linkedin-posts.json` in GitHub, click the pencil icon, and add entries
to the `posts` array with the fields below:

    {
      "url": "https://www.linkedin.com/posts/YOUR_PUBLIC_POST",
      "title": "My project update",
      "excerpt": "A short summary of this LinkedIn post.",
      "date": "2026-10-17"
    }

Use actual publicly visible LinkedIn post URLs. Commit the JSON file.
Manually added posts persist even when API sync is later activated.

References:
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- https://www.linkedin.com/help/linkedin/answer/a529065
