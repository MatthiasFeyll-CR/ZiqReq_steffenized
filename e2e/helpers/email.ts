import * as fs from "node:fs";
import * as path from "node:path";

/**
 * E2E email helpers.
 *
 * The gateway uses Django's filebased email backend, writing emails to
 * EMAIL_FILE_PATH (/tmp/e2e-emails/ inside the gateway container).
 *
 * When running Playwright outside Docker, this directory must be mounted
 * or accessible. The e2e-emails volume in docker-compose.e2e.yml is a
 * named volume — to read from the host, use `docker cp` or mount a
 * bind mount instead.
 *
 * For CI, consider using a bind mount: `./e2e/tmp-emails:/tmp/e2e-emails`
 */

const EMAIL_DIR = process.env.E2E_EMAIL_DIR ?? "/tmp/e2e-emails";

export interface ParsedEmail {
  filename: string;
  raw: string;
  to: string[];
  subject: string;
  body: string;
}

function parseEmailFile(filepath: string): ParsedEmail {
  const raw = fs.readFileSync(filepath, "utf-8");
  const lines = raw.split("\n");

  let subject = "";
  let to: string[] = [];
  let inBody = false;
  const bodyLines: string[] = [];

  for (const line of lines) {
    if (inBody) {
      bodyLines.push(line);
    } else if (line.trim() === "") {
      inBody = true;
    } else if (line.startsWith("Subject:")) {
      subject = line.slice("Subject:".length).trim();
    } else if (line.startsWith("To:")) {
      to = line
        .slice("To:".length)
        .split(",")
        .map((s) => s.trim());
    }
  }

  return {
    filename: path.basename(filepath),
    raw,
    to,
    subject,
    body: bodyLines.join("\n").trim(),
  };
}

/** List all captured emails. */
export function listEmails(): ParsedEmail[] {
  if (!fs.existsSync(EMAIL_DIR)) return [];

  return fs
    .readdirSync(EMAIL_DIR)
    .filter((f) => f.endsWith(".log"))
    .sort()
    .map((f) => parseEmailFile(path.join(EMAIL_DIR, f)));
}

/** Find emails sent to a specific recipient. */
export function findEmailsTo(recipient: string): ParsedEmail[] {
  return listEmails().filter((e) =>
    e.to.some((addr) => addr.toLowerCase().includes(recipient.toLowerCase())),
  );
}

/** Find emails with a subject matching a string or regex. */
export function findEmailsBySubject(subject: string | RegExp): ParsedEmail[] {
  return listEmails().filter((e) =>
    typeof subject === "string"
      ? e.subject.includes(subject)
      : subject.test(e.subject),
  );
}

/** Assert at least one email was sent to the given recipient. */
export function expectEmailTo(recipient: string): ParsedEmail {
  const emails = findEmailsTo(recipient);
  if (emails.length === 0) {
    throw new Error(
      `Expected at least one email to "${recipient}" but found none. ` +
        `Total emails: ${listEmails().length}`,
    );
  }
  return emails[0];
}

/** Assert at least one email with the given subject exists. */
export function expectEmailWithSubject(subject: string | RegExp): ParsedEmail {
  const emails = findEmailsBySubject(subject);
  if (emails.length === 0) {
    throw new Error(
      `Expected at least one email with subject matching "${subject}" but found none. ` +
        `Total emails: ${listEmails().length}`,
    );
  }
  return emails[0];
}

/** Clear all captured emails. */
export function clearEmails(): void {
  if (!fs.existsSync(EMAIL_DIR)) return;

  for (const file of fs.readdirSync(EMAIL_DIR)) {
    fs.unlinkSync(path.join(EMAIL_DIR, file));
  }
}
