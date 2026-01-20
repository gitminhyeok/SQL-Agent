import os
import sys
# 프로젝트 루트 경로를 sys.path에 추가 (모듈 import 문제 해결)
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.graph import build_graph


def main():
    print("SQL Agent Initializing...")

    app = build_graph()

    config = {"configurable": {"thread_id": "1"}}

    print("✅ Agent Ready! (Type 'quit' or 'q' to exit)")

    while True:
        try:
            user_input = input("\nUser (Q): ")
            if user_input.lower() in ["q", "quit", "exit"]:
                print("Bye!")
                break

            print("Agent is thinking...")
            events = app.stream(
                input={"messages": [("user", user_input)]},
                config=config,
                stream_mode="values"
            )

            for event in events:
                if "messages" in event:
                    last_msg = event["messages"][-1]

            snapshot = app.get_state(config)

            if snapshot.next:
                # 다음 단계 있다면 HITL
                print("\n [Confirmation Required]")
                print(f"Next Step: {snapshot.next}")
                
                current_state = snapshot.values
                generated_sql = current_state.get("sql_query", "N/A")

                print(f"Generated SQL: \033[96m{generated_sql}\033[0m")  # Cyan color

                confirm = input("Run this SQL? (y/n): ").strip().lower()

                if confirm == 'y':
                    print("Running...")
                    # None으로 안하면 어떻게 되지?
                    for event in app.stream(None, config, stream_mode='values'):
                        if "messages" in event:
                            # 최종 결과 출력
                            pass
                    
                    final_state = app.get_state(config).values
                    print(f"final_state: {final_state}")
                    if not final_state.get("error"):
                        print(final_state.get("query_result"))
                        print("SQL Agent quits.. ")
                        break
                    else:
                        print(f"{final_state}\n error occured retry.. " )
                else:
                    print("Operation cancelled by user.")

        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"error: {str(e)}")



if __name__ == "__main__":
    main()



