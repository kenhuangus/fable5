"""Part 9: redeem a fallback credit so a retry doesn't pay twice.

When you build the retry yourself (Ruby, PHP, raw HTTP, or any custom loop),
a manual re-send on the fallback model writes that model's prompt cache from
scratch, which costs more than a cache read. The fallback-credit beta returns
a one-time token that, echoed back on the retry, reprices the retry as if the
conversation had been on the fallback model all along.

This is the shape of the redemption. The SDK middleware and server-side
fallbacks do this for you; write it yourself only when neither is available.
"""
FALLBACK_BETA = "server-side-fallback-2026-06-01"
CREDIT_BETA = "fallback-credit-2026-06-01"


def refused(msg):
    return msg.stop_reason == "refusal"


def manual_fallback_with_credit(client, params, fallback_model):
    """Send on Fable 5; on a refusal, retry on the fallback model and redeem
    the credit. Returns the accepted message (or the final refusal)."""
    first = client.beta.messages.create(betas=[CREDIT_BETA], **params)
    if not refused(first):
        return first

    # The refusal carries a one-time credit token and a prefill-claim flag.
    details = first.stop_details
    token = getattr(details, "fallback_credit_token", None)
    has_prefill = getattr(details, "fallback_has_prefill_claim", False)
    if token is None:
        # No credit available; retry still works, it just writes cache fresh.
        retry = dict(params, model=fallback_model)
        return client.beta.messages.create(betas=[CREDIT_BETA], **retry)

    # Redemption requires an EXACT body match, so change only the model and
    # attach the credit. Do not strip or reorder anything else.
    retry = dict(params, model=fallback_model)
    return client.beta.messages.create(
        betas=[CREDIT_BETA],
        fallback_credit={"token": token, "has_prefill_claim": has_prefill},
        **retry,
    )


def served_by_sticky(msg):
    """A sticky-served turn has no fallback content block: identify it by a
    fallback_message iteration with no preceding message iteration for the
    requested model."""
    iters = msg.usage.iterations or []
    had_fallback = any(it.type == "fallback_message" for it in iters)
    had_requested = any(it.type == "message" for it in iters)
    return had_fallback and not had_requested
