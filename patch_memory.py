"""
Patch for app/MyAgent/main.py

1. Replaces the MemoryHook class so long-term memory works with Strands'
   list-of-blocks message format (the old one only handled plain strings, so
   nothing was ever saved or retrieved).
2. Strips <thinking>...</thinking> from the final response.

Run from the project root:   python3 patch_memory.py
A backup is written to app/MyAgent/main.py.bak
"""
import py_compile
import re
import shutil
import sys

PATH = "app/MyAgent/main.py"

NEW_CLASS = r'''import json, logging, re


class MemoryHook(HookProvider):
    """Long-term memory hook (handles Strands' list-of-blocks message format)."""

    CONTEXT_PREFIX = "Customer Context:\n"
    NAMESPACES = {
        "SEMANTIC": "cs_agent/{actorId}/facts",
        "USER_PREFERENCE": "cs_agent/{actorId}/preferences",
    }

    def __init__(self, actor_id, session_id):
        self.actor_id = actor_id
        self.session_id = session_id
        self.log = logging.getLogger("CSAI_Agent")

    @staticmethod
    def _text_of(content):
        """Plain text of a message (str or list of blocks); ignores injected context."""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    if block["text"].startswith(MemoryHook.CONTEXT_PREFIX):
                        continue
                    parts.append(block["text"])
            text = " ".join(parts)
        else:
            return ""
        text = re.sub(r"<thinking>.*?</thinking>\s*", "", text, flags=re.DOTALL).strip()
        # The runtime may hand the agent the whole payload as JSON; keep only the prompt
        if text.startswith("{"):
            try:
                obj = json.loads(text)
                if isinstance(obj, dict) and isinstance(obj.get("prompt"), str):
                    text = obj["prompt"].strip()
            except Exception:
                pass
        return text

    def retrieve_customer_context(self, event):
        try:
            messages = event.agent.messages
            if not messages:
                return
            last_msg = messages[-1]
            if last_msg.get("role") != "user":
                return
            query = self._text_of(last_msg.get("content"))
            if not query:
                return

            parts = []
            for strat, template in self.NAMESPACES.items():
                ns = template.replace("{actorId}", self.actor_id)
                try:
                    records = memory_client.retrieve_memories(
                        memory_id=MEMORY_ID, namespace=ns, query=query, top_k=5
                    )
                    for rec in records:
                        txt = rec.get("content", {}).get("text", "")
                        if txt:
                            parts.append(f"[{strat}] {txt}")
                except Exception as e:
                    self.log.warning("Memory retrieval failed for %s: %s", ns, e)

            if parts:
                block = {"text": self.CONTEXT_PREFIX + "\n".join(parts)}
                content = last_msg.get("content")
                if isinstance(content, list):
                    content.insert(0, block)
                else:
                    last_msg["content"] = [block, {"text": query}]
                self.log.info("Injected %d memory records into the prompt", len(parts))
        except Exception:
            self.log.exception("Error in retrieve hook")

    def save_support_interaction(self, event):
        try:
            user_q, reply = None, None
            for msg in reversed(event.agent.messages):
                text = self._text_of(msg.get("content"))
                if not text:
                    continue
                role = msg.get("role")
                if role == "assistant" and reply is None:
                    reply = text
                elif role == "user" and user_q is None and reply is not None:
                    user_q = text
                if user_q and reply:
                    break

            if user_q and reply:
                memory_client.create_event(
                    memory_id=MEMORY_ID,
                    actor_id=self.actor_id,
                    session_id=self.session_id,
                    messages=[(user_q, "USER"), (reply, "ASSISTANT")],
                )
                self.log.info("Saved interaction to memory")
            else:
                self.log.warning("Nothing to save to memory")
        except Exception:
            self.log.exception("Error in save hook")

    def register_hooks(self, registry, **kwargs):
        registry.add_callback(MessageAddedEvent, self.retrieve_customer_context)
        registry.add_callback(AfterInvocationEvent, self.save_support_interaction)
'''


def main():
    try:
        with open(PATH, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except FileNotFoundError:
        sys.exit(f"Cannot find {PATH}. Run this from the project root "
                 "(~/Project_starter/CustomerSupportAgent).")

    start = next((i for i, l in enumerate(lines) if l.startswith("class MemoryHook")), None)
    if start is None:
        sys.exit("Could not find 'class MemoryHook' in main.py - nothing changed.")

    # The class ends at the next line that starts at column 0 (code or comment)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        l = lines[j]
        if l.strip() and not l[0].isspace():
            end = j
            break

    shutil.copy(PATH, PATH + ".bak")
    new_lines = lines[:start] + NEW_CLASS.strip("\n").split("\n") + ["", ""] + lines[end:]
    text = "\n".join(new_lines)

    # Strip <thinking> tags from the final answer
    if "# strip thinking" not in text:
        pattern = r'^([ \t]*)return \{"response": resp_text\}'
        strip_line = r'resp_text = re.sub(r"<thinking>.*?</thinking>\s*", "", resp_text, flags=re.DOTALL).strip()  # strip thinking'
        text, n = re.subn(pattern,
                          lambda m: m.group(1) + strip_line + "\n" + m.group(0),
                          text, count=1, flags=re.M)
        if n == 0:
            print("NOTE: could not find 'return {\"response\": resp_text}' - "
                  "skipped the <thinking> cleanup (memory fix still applied).")

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(text)

    py_compile.compile(PATH, doraise=True)
    print(f"Replaced MemoryHook (old lines {start + 1}-{end}). Syntax OK.")
    print(f"Backup saved as {PATH}.bak")


if __name__ == "__main__":
    main()