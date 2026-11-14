/** Prevents responses from an older user request from replacing newer state. */
export class RequestEpoch {
  private current = 0

  begin(): number {
    this.current += 1
    return this.current
  }

  isCurrent(epoch: number): boolean {
    return epoch === this.current
  }

  invalidate(): void {
    this.current += 1
  }
}
