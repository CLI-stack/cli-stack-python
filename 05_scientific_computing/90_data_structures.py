"""
Script: Common Data Structures
What it does: Demonstrates essential data structures — Stack, Queue, Linked List.
Data structures are the building blocks of all software.
Understanding them helps you choose the right tool for the problem.
"""

from collections import deque  # double-ended queue (efficient for queues)

# =============================================================================
# STACK — Last In, First Out (LIFO)
# Like a stack of plates — you always add and remove from the top
# =============================================================================
print("=== STACK (Last In, First Out) ===")

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        """Add item to the top."""
        self.items.append(item)

    def pop(self):
        """Remove and return item from the top."""
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        """Look at the top item without removing it."""
        return self.items[-1] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

stack = Stack()
stack.push("first")
stack.push("second")
stack.push("third")

print(f"Stack after pushes: {stack.items}")
print(f"Peek: {stack.peek()}")     # look at top
print(f"Pop: {stack.pop()}")       # remove top
print(f"Stack now: {stack.items}")

# Use case: undo/redo, browser back button

# =============================================================================
# QUEUE — First In, First Out (FIFO)
# Like a line at a store — first person in, first person served
# =============================================================================
print("\n=== QUEUE (First In, First Out) ===")

class Queue:
    def __init__(self):
        self.items = deque()  # deque is efficient for queue operations

    def enqueue(self, item):
        """Add item to the back of the queue."""
        self.items.append(item)

    def dequeue(self):
        """Remove and return item from the front."""
        if not self.is_empty():
            return self.items.popleft()  # efficient O(1) operation
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

queue = Queue()
queue.enqueue("Customer 1")
queue.enqueue("Customer 2")
queue.enqueue("Customer 3")

print(f"Queue: {list(queue.items)}")
print(f"Serve: {queue.dequeue()}")  # first customer served
print(f"Queue: {list(queue.items)}")

# =============================================================================
# LINKED LIST — nodes connected by pointers
# =============================================================================
print("\n=== LINKED LIST ===")

class Node:
    """A single node in a linked list."""
    def __init__(self, data):
        self.data = data
        self.next = None  # pointer to the next node

class LinkedList:
    def __init__(self):
        self.head = None  # the first node

    def append(self, data):
        """Add a node at the end."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next  # traverse to the end
        current.next = new_node

    def display(self):
        """Print the linked list."""
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        print(" → ".join(elements) + " → None")

ll = LinkedList()
for val in [10, 20, 30, 40, 50]:
    ll.append(val)

print("Linked List:")
ll.display()
