import { fixture, path, Selector } from "testcafe";

const consentControlsDiv = Selector('.md-consent__controls');
const acceptButton = consentControlsDiv.find('button').withText('Accept');
const searchInput = Selector('input.md-search__input').withAttribute('placeholder', 'Search');
const searchResultItem = Selector('li.md-search-result__item');
const searchLabel = Selector('label.md-header__button.md-icon').withAttribute('for', '__search');

fixture("Verify site")
    .page`${path.join('http://127.0.0.1:8080/', process.env.CURRENT_BRANCH, '/#')}`
    .skipJsErrors();

test('Verify index file exists', async t => {
    await t
        .navigateTo`${path.join('http://127.0.0.1:8080/', process.env.CURRENT_BRANCH, '/index.html')}`;
})

test('Search for existence of incorrectly rendered fenced code blocks', async (t) => {
    await t.maximizeWindow();

    const acceptButtonExists = await acceptButton.exists;

    if (acceptButtonExists) {
        await t.click(acceptButton);
    }

    const searchLabelExists = await searchLabel.exists;
    const searchLabelVisible = await searchLabel.visible;

    if (searchLabelExists && searchLabelVisible) {
        await t.click(searchLabel);
    }

    await t.expect(searchInput.visible).ok();
    await t.click(searchInput);
    await t.typeText(searchInput, "```")

    const searchResultItemExists = await searchResultItem.exists;
    await t.expect(searchResultItemExists).notOk('Fenced code blocks exist in the search result and are therefore incorrectly rendered, failing the test');
})

test('Search for existence of incorrectly rendered admonitions', async (t) => {
    await t.maximizeWindow();

    const acceptButtonExists = await acceptButton.exists;

    if (acceptButtonExists) {
        await t.click(acceptButton);
    }

    const searchLabelExists = await searchLabel.exists;
    const searchLabelVisible = await searchLabel.visible;

    if (searchLabelExists && searchLabelVisible) {
        await t.click(searchLabel);
    }

    await t.expect(searchInput.visible).ok();
    await t.click(searchInput);
    await t.typeText(searchInput, "!!!")

    const searchResultItemExists = await searchResultItem.exists;
    await t.expect(searchResultItemExists).notOk('Admonitions exist in the search result and are therefore incorrectly rendered, failing the test');
})
