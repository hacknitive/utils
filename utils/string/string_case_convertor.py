from .constant import EnumCaseStrategy


case_strategy_function_dict = {
    EnumCaseStrategy.LOWER: lambda x: x.lower(),
    EnumCaseStrategy.UPPER: lambda x: x.upper(),
    EnumCaseStrategy.TITLE: lambda x: x.title(),
    EnumCaseStrategy.PASCAL: lambda x: x.title(),
}


def convert_string_case(
        text: str,
        split_char: str,
        join_char: str,
        case_strategy: None | EnumCaseStrategy,
) -> str:
    split_text = text.split(split_char)
    if case_strategy in (
            EnumCaseStrategy.LOWER,
            EnumCaseStrategy.UPPER,
            EnumCaseStrategy.TITLE,
            EnumCaseStrategy.PASCAL,
    ):
        function = case_strategy_function_dict[case_strategy]
        ready_text = list()
        for i in split_text:
            ready_text.append(function(i))

        return join_char.join(ready_text)

    elif case_strategy == EnumCaseStrategy.CAMEL:
        ready_text = [split_text[0].lower()]
        ready_text.extend([i.title() for i in split_text[1:]])
        return join_char.join(ready_text)


if __name__ == '__main__':
    result = convert_string_case(
        text='hEllo woRld',
        split_char=' ',
        join_char='',
        case_strategy=EnumCaseStrategy.CAMEL ,
    )
    print(result)
