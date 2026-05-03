from ..config.security import reset_web_password


def main() -> None:
    new_password = reset_web_password()
    print("")
    print("=" * 64)
    print("HF Bucket Sync - Password Reset")
    print("- A new login password has been generated.")
    print("- This password is only shown in this command output.")
    print(f"- New Password: {new_password}")
    print("=" * 64)
    print("")


if __name__ == "__main__":
    main()
